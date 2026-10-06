import csv
import os

students = [
    ("RA2311003020001", "Aakash Sharma", "CSE", 3, "CSE/K", 88, 92, 95, 84, 90),
    ("RA2311003020002", "Priya Sundaram", "CSE", 3, "CSE/K", 94, 96, 98, 91, 95),
    ("RA2311003020003", "Karthi Keyan", "CSE", 3, "CSE/K", 76, 82, 85, 70, 78),
    ("RA2311003020004", "Divya Narayanan", "CSE", 3, "CSE/K", 89, 91, 93, 85, 88),
    ("RA2311003020005", "Arvind Swaminathan", "CSE", 3, "CSE/K", 65, 71, 74, 58, 62),
    ("RA2311003020006", "Sneha Balaji", "CSE", 3, "CSE/K", 92, 89, 94, 88, 91),
    ("RA2311003020007", "Rahul Menon", "CSE", 3, "CSE/K", 54, 60, 68, 48, 55),
    ("RA2311003020008", "Swetha Krishnan", "CSE", 3, "CSE/K", 85, 88, 90, 82, 86),
    ("RA2311003020009", "Vignesh Rajan", "CSE", 3, "CSE/K", 72, 75, 80, 68, 74),
    ("RA2311003020010", "Ananya Iyer", "CSE", 3, "CSE/K", 96, 95, 99, 94, 97),
    ("RA2311003020011", "Harish Venkatesh", "CSE", 3, "CSE/K", 62, 65, 70, 55, 60),
    ("RA2311003020012", "Meera Chandrasekaran", "CSE", 3, "CSE/K", 91, 93, 95, 89, 92),
    ("RA2311003020013", "Roshan Joseph", "CSE", 3, "CSE/K", 45, 52, 60, 42, 50),
    ("RA2311003020014", "Pooja Ranganathan", "CSE", 3, "CSE/K", 83, 85, 88, 79, 84),
    ("RA2311003020015", "Sanjay Kumar", "CSE", 3, "CSE/K", 78, 80, 84, 75, 79),
    ("RA2311003020016", "Nithya Sridhar", "CSE", 3, "CSE/K", 87, 90, 92, 86, 89),
    ("RA2311003020017", "Deepa Mohan", "CSE", 3, "CSE/K", 68, 72, 75, 64, 70),
    ("RA2311003020018", "Gautham Prasad", "CSE", 3, "CSE/K", 59, 63, 67, 52, 58),
    ("RA2311003020019", "Keerthana Murali", "CSE", 3, "CSE/K", 95, 94, 97, 92, 94),
    ("RA2311003020020", "Ashwin Natarajan", "CSE", 3, "CSE/K", 81, 84, 86, 78, 82),
    ("RA2311003020021", "Pavithra Selvam", "CSE", 3, "CSE/K", 74, 78, 82, 71, 75),
    ("RA2311003020022", "Dinesh Varma", "CSE", 3, "CSE/K", 42, 55, 58, 46, 52),
    ("RA2311003020023", "Shalini Raghavan", "CSE", 3, "CSE/K", 88, 90, 92, 84, 87),
    ("RA2311003020024", "Naveen Prakash", "CSE", 3, "CSE/K", 67, 70, 73, 62, 66),
    ("RA2311003020025", "Lavanya Sethuraman", "CSE", 3, "CSE/K", 90, 92, 94, 88, 91),
    ("RA2311003020026", "Mithun Chander", "CSE", 3, "CSE/K", 58, 62, 65, 54, 60),
    ("RA2311003020027", "Shruti Subramanian", "CSE", 3, "CSE/K", 93, 95, 96, 90, 93),
    ("RA2311003020028", "Tejaswini B", "CSE", 3, "CSE/K", 79, 82, 85, 76, 80),
]

csv_path = r"C:\Users\pjeev\.gemini\antigravity-ide\scratch\student-result-analysis\data\student_results.csv"

header = ["Register_No", "Student_Name", "Department", "Semester", "Section", "DSA_21CSC201J", "OOP_21CSC202J", "APP_21CSC203P", "DM_21MTH201T", "COA_21CSC204J"]

with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(students)

print(f"Generated sample dataset with {len(students)} students at {csv_path}")
