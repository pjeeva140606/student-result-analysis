import io
import os
import matplotlib
matplotlib.use('Agg')  # Non-interactive background backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SUBJECT_CONFIG = [
    {
        "code": "21CSC201J",
        "short": "DSA",
        "name": "Data Structures and Algorithms",
        "col": "DSA_21CSC201J",
        "max": 100,
        "pass_mark": 50
    },
    {
        "code": "21CSC202J",
        "short": "OOP",
        "name": "Object Oriented Design & Programming",
        "col": "OOP_21CSC202J",
        "max": 100,
        "pass_mark": 50
    },
    {
        "code": "21CSC203P",
        "short": "APP",
        "name": "Advanced Programming Practices",
        "col": "APP_21CSC203P",
        "max": 100,
        "pass_mark": 50
    },
    {
        "code": "21MTH201T",
        "short": "DM",
        "name": "Discrete Mathematics",
        "col": "DM_21MTH201T",
        "max": 100,
        "pass_mark": 50
    },
    {
        "code": "21CSC204J",
        "short": "COA",
        "name": "Computer Organization and Architecture",
        "col": "COA_21CSC204J",
        "max": 100,
        "pass_mark": 50
    }
]

SUBJECT_COLS = [s["col"] for s in SUBJECT_CONFIG]

class StudentResultAnalyzer:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.load_data()

    def load_data(self):
        """Loads and cleans raw student data using Pandas."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Data file not found at {self.csv_path}")

        # Pandas reads CSV
        self.df = pd.read_csv(self.csv_path, dtype={"Register_No": str, "Semester": int})
        
        # Strip string whitespace
        for col in ["Register_No", "Student_Name", "Department", "Section"]:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()

        # Ensure all subject columns are numeric
        for col in SUBJECT_COLS:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").fillna(0).clip(0, 100)

        # Drop duplicates on Register_No if any
        self.df = self.df.drop_duplicates(subset=["Register_No"], keep="first")
        
        # Calculate derived metrics using Pandas vectorization
        self._compute_derived_metrics()
        return self.df

    def _compute_derived_metrics(self):
        """Module 2: Result Processing using Pandas vectorization."""
        if self.df.empty:
            return

        # 1. Total Marks (Sum across subject columns)
        self.df["Total"] = self.df[SUBJECT_COLS].sum(axis=1)

        # 2. Average Marks
        self.df["Average"] = self.df[SUBJECT_COLS].mean(axis=1).round(2)

        # 3. Percentage
        max_possible = len(SUBJECT_COLS) * 100
        self.df["Percentage"] = ((self.df["Total"] / max_possible) * 100).round(2)

        # 4. Pass/Fail Determination
        # A student passes only if they score >= pass_mark (50) in EVERY subject
        pass_conditions = [(self.df[s["col"]] >= s["pass_mark"]) for s in SUBJECT_CONFIG]
        all_passed = np.logical_and.reduce(pass_conditions)
        self.df["Result"] = np.where(all_passed, "Pass", "Fail")

        # 5. Letter Grade Determination (SRM Academic Grading Scheme)
        def assign_grade(row):
            if row["Result"] == "Fail":
                return "RA"  # Re-Appear
            pct = row["Percentage"]
            if pct >= 90:
                return "O"   # Outstanding
            elif pct >= 80:
                return "A+"  # Excellent
            elif pct >= 70:
                return "A"   # Very Good
            elif pct >= 60:
                return "B+"  # Good
            elif pct >= 50:
                return "B"   # Above Average
            else:
                return "RA"

        self.df["Grade"] = self.df.apply(assign_grade, axis=1)

        # 6. Rank Determination (Rank only passed students, sorted by Total desc)
        # Using Pandas rank method
        self.df["Rank"] = np.nan
        passed_mask = self.df["Result"] == "Pass"
        if passed_mask.any():
            self.df.loc[passed_mask, "Rank"] = (
                self.df.loc[passed_mask, "Total"]
                .rank(ascending=False, method="min")
                .astype(int)
            )

    def save_data(self):
        """Persists the base student data back to CSV."""
        base_cols = ["Register_No", "Student_Name", "Department", "Semester", "Section"] + SUBJECT_COLS
        try:
            self.df[base_cols].to_csv(self.csv_path, index=False)
        except (OSError, IOError, PermissionError):
            # In read-only serverless hosting like Vercel, changes remain in-memory in self.df
            pass

    def get_summary_statistics(self):
        """Returns high-level class summary metrics using Pandas aggregations."""
        if self.df.empty:
            return {
                "total_students": 0,
                "pass_count": 0,
                "fail_count": 0,
                "pass_percentage": 0.0,
                "class_average_pct": 0.0,
                "highest_score": 0,
                "highest_pct": 0.0,
                "highest_student": "N/A",
                "lowest_score": 0,
                "lowest_pct": 0.0,
                "lowest_student": "N/A",
                "std_dev_pct": 0.0
            }

        total_students = int(len(self.df))
        pass_count = int((self.df["Result"] == "Pass").sum())
        fail_count = int((self.df["Result"] == "Fail").sum())
        pass_pct = round((pass_count / total_students) * 100, 2) if total_students > 0 else 0.0
        class_avg_pct = round(float(self.df["Percentage"].mean()), 2)
        std_dev_pct = round(float(self.df["Percentage"].std()), 2) if total_students > 1 else 0.0

        # Highest scorer
        highest_idx = self.df["Total"].idxmax()
        highest_row = self.df.loc[highest_idx]

        # Lowest scorer
        lowest_idx = self.df["Total"].idxmin()
        lowest_row = self.df.loc[lowest_idx]

        return {
            "total_students": total_students,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_percentage": pass_pct,
            "class_average_pct": class_avg_pct,
            "highest_score": int(highest_row["Total"]),
            "highest_pct": float(highest_row["Percentage"]),
            "highest_student": f"{highest_row['Student_Name']} ({highest_row['Register_No']})",
            "lowest_score": int(lowest_row["Total"]),
            "lowest_pct": float(lowest_row["Percentage"]),
            "lowest_student": f"{lowest_row['Student_Name']} ({lowest_row['Register_No']})",
            "std_dev_pct": std_dev_pct
        }

    def get_subject_wise_analysis(self):
        """Subject-wise analysis using Pandas descriptive statistics."""
        analysis = []
        for s in SUBJECT_CONFIG:
            col = s["col"]
            series = self.df[col]
            avg_val = round(float(series.mean()), 2)
            max_val = int(series.max())
            min_val = int(series.min())
            std_val = round(float(series.std()), 2) if len(series) > 1 else 0.0
            pass_c = int((series >= s["pass_mark"]).sum())
            fail_c = int((series < s["pass_mark"]).sum())
            pass_p = round((pass_c / len(series)) * 100, 2) if len(series) > 0 else 0.0

            # Find top scorers in this subject
            top_scorer_row = self.df.loc[series.idxmax()]
            top_scorer = f"{top_scorer_row['Student_Name']} ({top_scorer_row['Register_No']})"

            analysis.append({
                "code": s["code"],
                "short": s["short"],
                "name": s["name"],
                "column": col,
                "average": avg_val,
                "highest": max_val,
                "lowest": min_val,
                "std_dev": std_val,
                "pass_count": pass_c,
                "fail_count": fail_c,
                "pass_percentage": pass_p,
                "top_scorer": top_scorer
            })
        return analysis

    def get_class_wise_analysis(self):
        """Class performance breakdown including grade distribution."""
        grade_dist = self.df["Grade"].value_counts().to_dict()
        all_grades = ["O", "A+", "A", "B+", "B", "RA"]
        formatted_grades = {g: int(grade_dist.get(g, 0)) for g in all_grades}

        pct_summary = self.df["Percentage"].describe().to_dict()
        total_summary = self.df["Total"].describe().to_dict()

        return {
            "grade_distribution": formatted_grades,
            "percentage_stats": {k: round(v, 2) for k, v in pct_summary.items()},
            "total_stats": {k: round(v, 2) for k, v in total_summary.items()}
        }

    def get_student_records(self, search="", filter_result="all", sort_by="Rank", sort_order="asc"):
        """Filters, searches, and sorts student records using Pandas queries."""
        filtered = self.df.copy()

        # Search by Name or Register Number
        if search:
            search_str = str(search).strip().lower()
            name_match = filtered["Student_Name"].str.lower().str.contains(search_str, na=False)
            reg_match = filtered["Register_No"].str.lower().str.contains(search_str, na=False)
            filtered = filtered[name_match | reg_match]

        # Filter by Result status
        if filter_result and filter_result != "all":
            filtered = filtered[filtered["Result"].str.lower() == filter_result.lower()]

        # Sorting
        if sort_by in filtered.columns:
            is_asc = (sort_order.lower() == "asc")
            # If sorting by rank, put NaN (Failures) at the end
            if sort_by == "Rank":
                filtered = filtered.sort_values(by="Rank", ascending=is_asc, na_position="last")
            else:
                filtered = filtered.sort_values(by=sort_by, ascending=is_asc)

        # Convert to records dictionary with native python types
        records = []
        for _, row in filtered.iterrows():
            item = row.to_dict()
            # Clean NaN for JSON serialization
            if pd.isna(item.get("Rank")):
                item["Rank"] = "-"
            else:
                item["Rank"] = int(item["Rank"])
            item["Total"] = int(item["Total"])
            item["Average"] = float(item["Average"])
            item["Percentage"] = float(item["Percentage"])
            for col in SUBJECT_COLS:
                item[col] = int(item[col])
            records.append(item)
        return records

    def add_student(self, data):
        """Adds a new student record and recalculates metrics."""
        reg_no = str(data.get("Register_No", "")).strip().upper()
        if not reg_no:
            raise ValueError("Register Number is required.")

        # Check duplicate
        if reg_no in self.df["Register_No"].values:
            raise ValueError(f"Student with Register Number {reg_no} already exists.")

        name = str(data.get("Student_Name", "")).strip()
        if not name:
            raise ValueError("Student Name is required.")

        dept = str(data.get("Department", "CSE")).strip()
        sem = int(data.get("Semester", 3))
        sec = str(data.get("Section", "CSE/K")).strip()

        row = {
            "Register_No": reg_no,
            "Student_Name": name,
            "Department": dept,
            "Semester": sem,
            "Section": sec
        }

        for s in SUBJECT_CONFIG:
            col = s["col"]
            val = float(data.get(col, 0))
            if val < 0 or val > 100:
                raise ValueError(f"Marks for {s['name']} must be between 0 and 100.")
            row[col] = val

        new_row_df = pd.DataFrame([row])
        self.df = pd.concat([self.df, new_row_df], ignore_index=True)
        self._compute_derived_metrics()
        self.save_data()
        return True

    def update_student(self, reg_no, data):
        """Updates an existing student record."""
        reg_no = str(reg_no).strip().upper()
        if reg_no not in self.df["Register_No"].values:
            raise ValueError(f"Student {reg_no} not found.")

        idx = self.df.index[self.df["Register_No"] == reg_no].tolist()[0]

        if "Student_Name" in data and str(data["Student_Name"]).strip():
            self.df.at[idx, "Student_Name"] = str(data["Student_Name"]).strip()
        if "Department" in data:
            self.df.at[idx, "Department"] = str(data["Department"]).strip()
        if "Semester" in data:
            self.df.at[idx, "Semester"] = int(data["Semester"])
        if "Section" in data:
            self.df.at[idx, "Section"] = str(data["Section"]).strip()

        for s in SUBJECT_CONFIG:
            col = s["col"]
            if col in data:
                val = float(data[col])
                if val < 0 or val > 100:
                    raise ValueError(f"Marks for {s['name']} must be between 0 and 100.")
                self.df.at[idx, col] = val

        self._compute_derived_metrics()
        self.save_data()
        return True

    def delete_student(self, reg_no):
        """Deletes a student record."""
        reg_no = str(reg_no).strip().upper()
        if reg_no not in self.df["Register_No"].values:
            raise ValueError(f"Student {reg_no} not found.")

        self.df = self.df[self.df["Register_No"] != reg_no].reset_index(drop=True)
        self._compute_derived_metrics()
        self.save_data()
        return True

    def import_csv(self, file_storage, mode="replace"):
        """Imports CSV file using Pandas, validates schema, and updates dataset."""
        uploaded_df = pd.read_csv(file_storage)
        
        # Check required columns
        required_cols = ["Register_No", "Student_Name"] + SUBJECT_COLS
        missing = [c for c in required_cols if c not in uploaded_df.columns]
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

        # Ensure default metadata columns
        if "Department" not in uploaded_df.columns:
            uploaded_df["Department"] = "CSE"
        if "Semester" not in uploaded_df.columns:
            uploaded_df["Semester"] = 3
        if "Section" not in uploaded_df.columns:
            uploaded_df["Section"] = "CSE/K"

        # Validate marks range
        for col in SUBJECT_COLS:
            uploaded_df[col] = pd.to_numeric(uploaded_df[col], errors="coerce").fillna(0).clip(0, 100)

        uploaded_df["Register_No"] = uploaded_df["Register_No"].astype(str).str.strip().str.upper()
        uploaded_df["Student_Name"] = uploaded_df["Student_Name"].astype(str).str.strip()

        if mode == "append":
            # Exclude duplicate Register_No that already exist
            existing_regs = set(self.df["Register_No"].values)
            new_records = uploaded_df[~uploaded_df["Register_No"].isin(existing_regs)]
            self.df = pd.concat([self.df, new_records], ignore_index=True)
        else:
            self.df = uploaded_df.drop_duplicates(subset=["Register_No"], keep="first").reset_index(drop=True)

        self._compute_derived_metrics()
        self.save_data()
        return len(self.df)

    def export_processed_csv(self):
        """Exports the analyzed dataframe with all computed fields as CSV."""
        export_cols = (
            ["Rank", "Register_No", "Student_Name", "Department", "Semester", "Section"]
            + SUBJECT_COLS
            + ["Total", "Average", "Percentage", "Result", "Grade"]
        )
        # Sort by Rank or Percentage descending
        sorted_df = self.df.sort_values(by="Total", ascending=False)
        output = io.StringIO()
        sorted_df[export_cols].to_csv(output, index=False)
        return output.getvalue()

    # -------------------------------------------------------------
    # MODULE 4: DATA VISUALIZATION USING MATPLOTLIB
    # -------------------------------------------------------------

    def _setup_figure_style(self):
        """Applies clean academic aesthetic parameters."""
        plt.rcParams['font.sans-serif'] = 'Segoe UI, Arial, sans-serif'
        plt.rcParams['axes.edgecolor'] = '#cbd5e1'
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['grid.color'] = '#f1f5f9'
        plt.rcParams['grid.linestyle'] = '--'

    def generate_chart_subject_averages(self):
        """Chart 1: Subject-wise Average Marks Bar Chart."""
        self._setup_figure_style()
        fig, ax = plt.subplots(figsize=(8, 4.8), dpi=120)
        
        subjects = [s["short"] for s in SUBJECT_CONFIG]
        averages = [round(float(self.df[s["col"]].mean()), 2) for s in SUBJECT_CONFIG]
        colors = ['#1e40af', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd']

        bars = ax.bar(subjects, averages, color=colors, width=0.55, edgecolor='#1e3a8a', linewidth=1)
        ax.axhline(50, color='#dc2626', linestyle='--', linewidth=1.2, label='Passing Benchmark (50%)')

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1e293b')

        ax.set_title('Subject-wise Average Marks (Class CSE/K)', fontsize=12, fontweight='bold', pad=15, color='#0f172a')
        ax.set_xlabel('Subject Code & Abbreviation', fontsize=10, fontweight='bold', labelpad=10, color='#334155')
        ax.set_ylabel('Average Marks (Out of 100)', fontsize=10, fontweight='bold', labelpad=10, color='#334155')
        ax.set_ylim(0, 105)
        ax.grid(axis='y', alpha=0.7)
        ax.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def generate_chart_student_comparison(self):
        """Chart 2: Student Performance Comparison (All students Percentage bar chart)."""
        self._setup_figure_style()
        fig, ax = plt.subplots(figsize=(11, 5), dpi=120)

        # Sort by Percentage descending
        sorted_df = self.df.sort_values(by="Percentage", ascending=False).reset_index()
        names = [f"{row['Student_Name'][:12]}" for _, row in sorted_df.iterrows()]
        pcts = sorted_df["Percentage"].values
        colors = ['#059669' if r == 'Pass' else '#e11d48' for r in sorted_df["Result"].values]

        bars = ax.bar(range(len(names)), pcts, color=colors, width=0.65, edgecolor='#0f172a', linewidth=0.5)
        ax.axhline(50, color='#dc2626', linestyle='--', linewidth=1.2, label='Pass Benchmark (50%)')
        class_avg = self.df["Percentage"].mean()
        ax.axhline(class_avg, color='#2563eb', linestyle=':', linewidth=1.5, label=f'Class Mean ({class_avg:.1f}%)')

        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=65, ha='right', fontsize=8, color='#334155')
        ax.set_title('Student Performance Comparison (Percentage %)', fontsize=12, fontweight='bold', pad=15, color='#0f172a')
        ax.set_ylabel('Overall Percentage (%)', fontsize=10, fontweight='bold', color='#334155')
        ax.set_ylim(0, 105)
        ax.grid(axis='y', alpha=0.7)
        ax.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def generate_chart_pass_fail_distribution(self):
        """Chart 3: Pass vs Fail Distribution Pie Chart."""
        self._setup_figure_style()
        fig, ax = plt.subplots(figsize=(6.5, 4.8), dpi=120)

        pass_c = int((self.df["Result"] == "Pass").sum())
        fail_c = int((self.df["Result"] == "Fail").sum())
        counts = [pass_c, fail_c]
        labels = [f"Passed ({pass_c})", f"Re-appear / Failed ({fail_c})"]
        colors = ['#10b981', '#f43f5e']

        wedges, texts, autotexts = ax.pie(
            counts,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            wedgeprops={'edgecolor': '#ffffff', 'linewidth': 2, 'width': 0.65}, # donut
            textprops={'fontsize': 10, 'fontweight': 'bold', 'color': '#1e293b'}
        )

        for autotext in autotexts:
            autotext.set_color('#ffffff')
            autotext.set_fontsize(11)
            autotext.set_weight('bold')

        ax.set_title('Pass vs Fail Distribution (Class CSE/K)', fontsize=12, fontweight='bold', pad=15, color='#0f172a')
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def generate_chart_percentage_distribution(self):
        """Chart 4: Percentage Distribution Histogram with Grade Bands."""
        self._setup_figure_style()
        fig, ax = plt.subplots(figsize=(8, 4.8), dpi=120)

        percentages = self.df["Percentage"].values
        bins = [40, 50, 60, 70, 80, 90, 100]

        counts, bin_edges, patches = ax.hist(
            percentages, bins=bins, color='#3b82f6', edgecolor='#1e3a8a', linewidth=1, rwidth=0.85
        )

        for count, edge in zip(counts, bin_edges):
            if count > 0:
                ax.annotate(f"{int(count)}",
                            xy=(edge + 5, count),
                            xytext=(0, 4),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1e293b')

        # Grade Band labels
        grade_labels = ["RA (<50)", "B (50-59)", "B+ (60-69)", "A (70-79)", "A+ (80-89)", "O (90-100)"]
        ax.set_xticks([45, 55, 65, 75, 85, 95])
        ax.set_xticklabels(grade_labels, fontsize=9, color='#334155')

        ax.set_title('Class Percentage Distribution by Grade Interval', fontsize=12, fontweight='bold', pad=15, color='#0f172a')
        ax.set_xlabel('Grade Range & Score Interval (%)', fontsize=10, fontweight='bold', labelpad=10, color='#334155')
        ax.set_ylabel('Number of Students', fontsize=10, fontweight='bold', labelpad=10, color='#334155')
        ax.grid(axis='y', alpha=0.7)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def generate_chart_subject_comparison(self):
        """Chart 5: Subject Performance Comparison (Grouped Bar: Min, Avg, Max)."""
        self._setup_figure_style()
        fig, ax = plt.subplots(figsize=(9, 5), dpi=120)

        subjects = [s["short"] for s in SUBJECT_CONFIG]
        mins = [int(self.df[s["col"]].min()) for s in SUBJECT_CONFIG]
        avgs = [round(float(self.df[s["col"]].mean()), 1) for s in SUBJECT_CONFIG]
        maxs = [int(self.df[s["col"]].max()) for s in SUBJECT_CONFIG]

        x = np.arange(len(subjects))
        width = 0.25

        rects1 = ax.bar(x - width, mins, width, label='Lowest Mark', color='#f87171', edgecolor='#b91c1c')
        rects2 = ax.bar(x, avgs, width, label='Average Mark', color='#60a5fa', edgecolor='#1d4ed8')
        rects3 = ax.bar(x + width, maxs, width, label='Highest Mark', color='#34d399', edgecolor='#047857')

        # Add benchmark
        ax.axhline(50, color='#dc2626', linestyle='--', linewidth=1, alpha=0.7, label='Pass Threshold (50)')

        ax.set_title('Subject Performance Comparison: Minimum, Average & Maximum', fontsize=12, fontweight='bold', pad=15, color='#0f172a')
        ax.set_xlabel('Subject Code', fontsize=10, fontweight='bold', labelpad=10, color='#334155')
        ax.set_ylabel('Marks (Out of 100)', fontsize=10, fontweight='bold', labelpad=10, color='#334155')
        ax.set_xticks(x)
        ax.set_xticklabels(subjects, fontsize=10, fontweight='bold')
        ax.set_ylim(0, 110)
        ax.grid(axis='y', alpha=0.7)
        ax.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def generate_chart_top_performers(self):
        """Chart 6: Top Performing Students Bar Chart (Top 8 Rankers)."""
        self._setup_figure_style()
        fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=120)

        # Get top 8 passed students
        top_students = (
            self.df[self.df["Result"] == "Pass"]
            .sort_values(by="Total", ascending=True)  # ascending for horizontal bar chart
            .tail(8)
        )

        names = [f"{row['Student_Name']} ({row['Register_No'][-4:]})" for _, row in top_students.iterrows()]
        pcts = top_students["Percentage"].values

        bars = ax.barh(names, pcts, color='#2563eb', height=0.55, edgecolor='#1e3a8a')

        for bar in bars:
            width = bar.get_width()
            ax.annotate(f'{width:.1f}%',
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(5, 0),
                        textcoords="offset points",
                        ha='left', va='center', fontsize=9, fontweight='bold', color='#1e293b')

        ax.set_title('Top Performing Students (Class Rankers)', fontsize=12, fontweight='bold', pad=15, color='#0f172a')
        ax.set_xlabel('Overall Percentage (%)', fontsize=10, fontweight='bold', labelpad=10, color='#334155')
        ax.set_xlim(0, 105)
        ax.grid(axis='x', alpha=0.7)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf
