## Frappe ERD Generator

ERD generator for frappe doctypes

#### Download

```bash
$ bench get-app https://github.com/The-Commit-Company/frappe_er_generator.git
```

#### Install

```bash
$ bench --site site_name install-app frappe_er_generator
```

1. Call `get_erd` function for generating ERD by passing list of doctypes as argument.

path = `api/method/frappe_er_generator.frappe_er_generator.er_generator.get_erd?doctypes = ["DocType1", "DocType2"]`

2. Call `get_whitelist_methods_in_app` function for fetching all whitelisted methods in app, by passing app name as argument. `app` is argument name.

#### Note:

If got error while calling API - "RuntimeError: Make sure the Graphviz executables are on your system's path" after installing Graphviz 2.38, them install graphviz in macos using brew

```bash
$ brew install graphviz
```

#### Output:

1. ERD in PNG format

![erd](https://user-images.githubusercontent.com/59503001/231471200-7717c3d4-75f5-45b2-8c2c-84d07ddd865b.png)


2. Output of `get_whitelist_methods_in_app`

<img width="1440" alt="image" src="https://user-images.githubusercontent.com/59503001/231189481-3d0a39b9-3cf4-49e1-a456-706ff700138f.png">

#### License

MIT

#### ERD generator for Frappe Doctypes Tài liệu hướng dẫn sử dụng tạo ERD (Entity Relationship Diagram) cho các Doctypes của Frappe.


#### I. Các API có thể gọi 

### Bước 1: Lấy doctypes từ 1 app: get_doctype_from_app

Tham số: app {Tên app}

Ví dụ:

dev.wellspringsaigon.edu.vn/api/method/frappe_er_generator.frappe_er_generator.er_generator.get_doctype_from_app?app=parent_portal

### Kết quả trả về có dạng:

{ "message": [ { "doctype": [ "SIS PTC Time Slot", "SIS PTC Registration", "SIS PTC Form", "SIS PTC Settings", "SIS ECA Form", "SIS Reenroll Form", "SIS HBTN Form Score Template", "SIS HBTN Form", "SIS HBTN Score Criterion", "SIS HBTN Student Application", "SIS HBTN Application Score", "SIS HBTN Score Group", "SIS HBTN Settings", "SIS ECA Settings", "SIS ECA Course Class", "SIS ECA Application", "SIS ECA Group", "SIS Student", "SIS Subject", "SIS Academic Program", "SIS ECA CC Student List", "SIS ECA Student Registration", "SIS ECA CC Allowed Student", "SIS ECA Form Group Rule", "SIS Person", "SIS School Year", "SIS School Feed", "SIS Staff", "SIS Department", "SIS Attendance Log School Class", "SIS Reenroll Payment Discount", "SIS Family", "SIS Reenroll Form Submission", "SIS School Class", "SIS Student Report Card", "SIS School Year Term", "SIS School Grade Level", "SIS Policy Document", "SIS Feedback", "SIS Academic Year Event", "SIS Attendance Log Person", "SIS Attendance Log Course Class", "SIS Settings", "SIS Class Feed", "SIS Menu", "SIS Course Class", "SIS Timetable Scheduling Tool", "SIS Course", "SIS Guardian Registry", "SIS School Class Person", "SIS Course Class Person", "SIS Timetable Day Row Class", "SIS Timetable Column Row", "SIS Timetable Day", "SIS Timetable", "SIS Timetable Day Date", "SIS Timetable Column", "SIS Class Feed Photo", "SIS Floor", "SIS Building", "SIS Room", "SIS Family Guardian", "SIS Family Child" ], "module": "SIS" }, { "doctype": [ "PP Variable Setting", "PP User", "PP Message", "PP Channel Member", "PP Channel" ], "module": "Parent Portal" } ] } lấy danh sách doctype ở trên truyền vào cho api ở bước 2

### Bước 2: Khi đã có danh sách doctypes ở dạng json của các module trong app, lần lượt truyền vào: get_erd

Tham số: doctypes [json danh sách doctype]

Ví dụ:

https://dev.wellspringsaigon.edu.vn/api/method/frappe_er_generator.frappe_er_generator.er_generator.get_erd?doctypes=[“Doctype 1”,”Doctype 2”]

Kết quả trả về sẽ có dạng:

{ "message": { "message": "ERD generated successfully", "file_path": "/files/erd_20250506_141056.png", "file_url": "https://dev.wellspringsaigon.edu.vn/files/erd_20250506_141056.png" } } lấy file_url ra để sử dụng
