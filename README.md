# Student Result Analysis System Using Pandas and Matplotlib

**College Academic Project — Advanced Programming Practices (21CSC203P)**  
*SRM Institute of Science and Technology, Ramapuram, Chennai*  
*Department of Computer Science and Engineering*  
*II Year / III Semester &bull; Class / Sec: CSE/K*

---

## 📌 Project Overview

The **Student Result Analysis System** is an automated academic performance analysis and visualization dashboard built using **Python**, **Pandas**, **Matplotlib**, and **Flask**.

Designed specifically for university departmental review, this system processes semester examination results, calculates comprehensive academic metrics (total marks, percentage, class rank, pass/fail status, and SRM letter grades), and visualizes the results through dynamic Matplotlib graphical charts.

---

## 🎯 Key Features & Modules

### 1. Student Data Management (Module 1)
- Initialized with **28 realistic SRM CSE/K student records** across 5 semester subjects:
  - `21CSC201J`: Data Structures and Algorithms (DSA)
  - `21CSC202J`: Object Oriented Design & Programming (OOP)
  - `21CSC203P`: Advanced Programming Practices (APP)
  - `21MTH201T`: Discrete Mathematics (DM)
  - `21CSC204J`: Computer Organization and Architecture (COA)
- Complete **CRUD operations**: Add new student records, edit marks, and delete students.
- **Real-time search & filtering**: Search by student name or register number, filter by result status (*Pass* / *Re-appear*), and multi-criteria sorting.
- **Semester Grade Sheet / Transcript Modal**: View and print official semester mark sheets with letter grades and class rank.

### 2. Result Processing Engine (Module 2)
- Automated vectorized evaluation using Pandas.
- Strict pass criteria: $\ge 50$ marks in each of the 5 courses.
- SRM Academic Grading Scheme:
  - `O`: $\ge 90\%$ (Outstanding)
  - `A+`: $80\% - 89\%$ (Excellent)
  - `A`: $70\% - 79\%$ (Very Good)
  - `B+`: $60\% - 69\%$ (Good)
  - `B`: $50\% - 59\%$ (Above Average)
  - `RA`: $< 50\%$ or failed in any subject (Re-appear)

### 3. Data Analysis Module (Module 3)
- **Subject-wise analysis**: Mean, maximum score, minimum score, standard deviation, pass rate, and top scorer identification.
- **Class descriptive statistics**: Pandas `.describe()` breakdown ($N$, Mean, Std Dev, Min, 25% Q1, Median, 75% Q3, Max).
- **Grade distribution**: Frequency count of students across all letter grades.

### 4. Data Visualization Module (Module 4)
Six dynamic Matplotlib charts rendered using the headless `Agg` engine:
1. **Subject-wise Average Marks**: Bar chart with 50% passing benchmark.
2. **Student Performance Comparison**: Percentage bar chart with class mean line and pass/fail color-coding.
3. **Pass vs Fail Distribution**: Donut pie chart with percentages and counts.
4. **Percentage Distribution**: Frequency histogram categorized by grade intervals.
5. **Subject Performance Comparison**: Grouped bar chart comparing Minimum, Average, and Maximum marks.
6. **Top Performing Students**: Horizontal ranking chart of top rankers.

### 5. CSV Import & Export (Module 5)
- Drag-and-drop CSV upload with schema validation.
- Export processed results spreadsheet with all calculated columns.
- Download sample CSV template.
- One-click reset to factory sample data.

### 6. SRM APP Review Documentation
Full academic review presentation structure embedded directly in the application:
1. Title / Project Information
2. Abstract
3. Scope and Motivation
4. Architecture Diagram
5. ER Diagram
6. Software Tools & Specifications
7. List of Modules
8. Module Explanation (Modules 1 to 5)
9. Screenshots Gallery
10. Conclusion
11. References

---

## 🛠️ Technology Stack

- **Backend / Processing**: Python 3.13, Pandas, Matplotlib, Flask
- **Frontend**: HTML5, Vanilla CSS3 (Academic Theme), Vanilla JavaScript (ES6+)
- **Data Persistence**: CSV with Pandas DataFrame in-memory caching
- **Deployment**: Vercel Serverless

---

## 🚀 Local Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pjeeva140606/student-result-analysis.git
   cd student-result-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 📜 Academic Attribution

Developed for:
- **Institution**: SRM Institute of Science and Technology, Ramapuram, Chennai
- **Department**: Department of Computer Science and Engineering
- **Course**: 21CSC203P – Advanced Programming Practices
- **Class / Section**: CSE / K
