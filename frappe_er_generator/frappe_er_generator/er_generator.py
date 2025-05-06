import frappe
import os
from frappe.config import get_modules_from_app, get_modules_from_all_apps
import graphviz


def get_apps():
    # get all the apps installed on the bench
    return frappe.get_all_apps()


@frappe.whitelist()
def get_all_modules_from_all_apps():
    # get all the modules from all the apps installed on the bench
    app_module_object = {}
    app_module = get_modules_from_all_apps()
    for i in app_module:
        if i.get('app') in app_module_object.keys():
            app_module_object[i.get('app')].append(i.get('module_name'))
        else:
            app_module_object[i.get('app')] = [i.get('module_name')]
    return app_module_object


@frappe.whitelist()
def get_doctype_from_app(app):
    doctype_list = []
    module = get_modules_from_app(app)
    for i in module:
        doctype_list.append(get_doctypes_from_module(i.module_name))
    return doctype_list


@frappe.whitelist()
def get_doctypes_from_module(module):
    return {'doctype': [doctype['name'] for doctype in frappe.get_list('DocType', filters={'module': module})], 'module': module}


@frappe.whitelist()
def get_doctype_json():
    # return frappe.get_doc('DocType', 'Lead').as_dict()
    return frappe.get_meta('Lead').as_dict()


"""
@api {get} /api/method/frappe_er_generator.er_generator.get_erd Get ERD
@apiName get_erd
@apiQuery {String} doctypes Doctypes

@apiSuccess {String} message Success {Generate ERD with name erd.png}
"""


@frappe.whitelist()
def get_erd(doctypes):
    try:
        # Log input for debugging
        #frappe.log_error(f"Received doctypes: {doctypes}", "ERD Debug")

        # Parse doctypes if it's a JSON string
        if isinstance(doctypes, str):
            try:
                doctypes = frappe.parse_json(doctypes)
            except ValueError:
                frappe.throw("Invalid doctypes format. Expected a JSON array, e.g., ['Employee', 'Department']")

        # Validate doctypes is a list
        if not isinstance(doctypes, list):
            frappe.throw("doctypes must be a list of DocType names")

        # Validate each DocType exists
        for doctype in doctypes:
            if not frappe.db.exists("DocType", doctype):
                frappe.throw(f"DocType {doctype} not found")

        # Initialize lists
        json_list = []
        link_list = []
        table_list = []
        connections_string_list = []
        fetch_from_string_list = []

        # Get metadata and link fields
        for doctype in doctypes:
            data = frappe.get_meta(doctype).as_dict()
            json_list.append(data)
            link_list += [{**x, 'doctype': data.get('name')}
                          for x in data.get('fields') if x['fieldtype'] == 'Link']

        # Generate tables and connections
        for doctype_data in json_list:
            table, connection_list, fetch_from = get_table(
                doctype_data, link_list, doctypes)
            table_list.append(table)
            connections_string_list += connection_list
            fetch_from_string_list += fetch_from

        # Generate and create graph
        # Generate and create graph
        graph_string = get_graph_string(
            table_list, connections_string_list, fetch_from_string_list)
        file_path = create_graph(graph_string)

        # Return file path or URL
        file_url = frappe.utils.get_url(file_path) if file_path.startswith('/files') else file_path
        return {
            "message": "ERD generated successfully",
            "file_path": file_path,
            "file_url": file_url
        }

    except Exception as e:
        frappe.log_error(f"Error in get_erd: {str(e)}", "ERD Error")
        frappe.throw(f"Failed to generate ERD: {str(e)}")

def create_graph(graph_string):
    # Create graph from graph_string
    graph = graphviz.Source(graph_string)
    graph.format = 'png'

    # Define file path in public/files
    file_name = f"erd_{frappe.utils.now_datetime().strftime('%Y%m%d_%H%M%S')}.png"
    file_path = frappe.get_site_path('public', 'files', file_name)

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Render graph to file
    graph.render(filename=file_path[:-4], format='png', view=False, cleanup=True)

    # Save file record in Frappe
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "file_url": f"/files/{file_name}",
        "is_private": 0,
        "attached_to_doctype": None,
        "attached_to_name": None
    })
    file_doc.save()

    return f"/files/{file_name}"

def get_table(data, link_list, doctypes):
    # data is doctype json data (meta data) link_list is list of all Link fieldtype fields objects and doctypes is list of all doctypes
    # get_table function will return table string, connection_list, fetch_from

    # table_element_list is row of the table in the ERD in string format.
    table_element_list = []

    # remove_fieldtype is list of fieldtype which we don't want to show in the ERD.
    remove_fieldtype = ['Column Break', 'Section Break', 'Tab Break']

    # connection_list is list of all the Link connections in the ERD in string format.
    connection_list = []

    # fetch_from is list of all the fetch_from connections in the ERD in string format just like connection_list.
    fetch_from = []
    for field in data.get("fields"):
        if field.get('fieldtype') not in remove_fieldtype:
            # add each field as a row in the table
            if field.get('is_custom_field'):
                table_element_list.append(
                    f'<tr><td bgcolor="#FEF3E2" port="{field.get("fieldname")}">{field.get("label")}</td></tr>')
            else:
                table_element_list.append(
                    f'<tr><td port="{field.get("fieldname")}">{field.get("label")}</td></tr>')
        if field.get("fieldtype") == "Link":
            # get_connection function will return connection string
            connection_data = get_connection(field, data.get("name"), doctypes)
            if connection_data:
                connection_list.append(connection_data)
        if field.get("fetch_from") != None:
            # get_fetch_from function will return fetch_from string
            fetch_data = get_fetch_from(field, data.get(
                "name"), link_list, doctypes)
            if fetch_data:
                fetch_from.append(fetch_data)

    table_elements = "\n".join(table_element_list)

    table = f"""{"".join(c if c.isalnum() else "_" for c in data.get("name")).lower()} [label=<
    <table border="0" cellborder="1" cellspacing="0">
    <tr><td port = "name"><b>{data.get("name")}</b></td></tr>
    {table_elements}
    </table>>];"""

    return table, connection_list, fetch_from


def get_connection(data, doctype_name, doctypes):
    # data is Link fieldtype field object, doctype_name is doctype name and doctypes is list of all doctypes
    # get_connection function will return connection string
    if data.get("options") in doctypes:
        connection_string = f"""{"".join(c if c.isalnum() else "_" for c in doctype_name).lower()}:{data.get('fieldname')} -> {"".join(c if c.isalnum() else "_" for c in data.get("options")).lower()}:name;"""
        return connection_string

    return None


def get_fetch_from(data, doctype_name, link_list, doctypes):
    # data is field object of doctype which have fetch_from field, doctype_name is doctype name, link_list is list of all Link fieldtype fields objects and doctypes is list of all doctypes
    # get_fetch_from function will return fetch_from string
    fetch_from = data.get("fetch_from")
    if not fetch_from or '.' not in fetch_from:
        return None

    fetch_field = fetch_from.split(".")[0]
    fetch_link_object = next((x for x in link_list if x.get("fieldname") == fetch_field), None)
    
    if not fetch_link_object:
        frappe.log_error(
            f"Fetch field '{fetch_field}' in fetch_from '{fetch_from}' not found in link_list for doctype '{doctype_name}'",
            "ERD Debug"
        )
        return None

    if fetch_link_object.get('options') in doctypes:
        fetch_string = f"""{"".join(c if c.isalnum() else "_" for c in fetch_link_object.get('doctype')).lower()}:{data.get('fieldname')} -> {"".join(c if c.isalnum() else "_" for c in fetch_link_object.get('options')).lower()}:{fetch_from.split(".")[1]} [style="dashed"];"""
        return fetch_string

    return None


def get_graph_string(table_list, connections_string_list, fetch_from_string_list):
    # join all the table, connection and fetch_from string to get graph string
    table_string = "\n\n".join(table_list)
    connections_string = "\n".join(connections_string_list)
    fetch_from_string = "\n".join(fetch_from_string_list)
    graph_string = f"""
        digraph {{
            graph [pad="0.5", nodesep="0.5", ranksep="2",legend="Fetch from\\l\\nNormal Link\\l"];
            node [shape=plain]
            rankdir=LR;

            {table_string}

        {connections_string}

        {fetch_from_string}

        subgraph cluster_01 {{ 
            label = "Legend";
            key [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">
            <tr><td align="left" port="i1">Link</td></tr>
            <tr><td align="left" port="i2">Fetch from</td></tr>
            <tr><td>Custom Fields</td>
            <td cellpadding="2"><table border="1" cellpadding="8" cellspacing="0" >
            <tr><td bgcolor="#FEF3E2"></td></tr></table></td></tr>
            </table>>]
            key2 [label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">
            <tr><td port="i1">&nbsp;</td></tr>
            <tr><td port="i2">&nbsp;</td></tr>
            </table>>]
            key:i1:e -> key2:i1:w 
            key:i2:e -> key2:i2:w [style=dashed]
        }}
        }}
    """
    return graph_string
