import os
import io
from flask import Flask, render_template, request, jsonify, send_file, Response
from analyzer import StudentResultAnalyzer, SUBJECT_CONFIG, SUBJECT_COLS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates")
)
app.config["SECRET_KEY"] = "srm-app-cse-k-2026-key"

DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "student_results.csv")
BACKUP_CSV_PATH = os.path.join(DATA_DIR, "student_results_backup.csv")

# Initialize Analyzer
analyzer = StudentResultAnalyzer(CSV_PATH)

# Save backup copy if doesn't exist
try:
    if not os.path.exists(BACKUP_CSV_PATH):
        analyzer.df.to_csv(BACKUP_CSV_PATH, index=False)
except Exception:
    pass

@app.route("/")
def index():
    return render_template("index.html", subjects=SUBJECT_CONFIG)

# ---------------- API ENDPOINTS ----------------

@app.route("/api/summary", methods=["GET"])
def get_summary():
    """Returns class summary statistics calculated via Pandas."""
    try:
        stats = analyzer.get_summary_statistics()
        return jsonify({"status": "success", "data": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/students", methods=["GET"])
def get_students():
    """Returns filtered, searched, and sorted student records."""
    try:
        search = request.args.get("search", "")
        filter_result = request.args.get("filter_result", "all")
        sort_by = request.args.get("sort_by", "Rank")
        sort_order = request.args.get("sort_order", "asc")

        records = analyzer.get_student_records(
            search=search,
            filter_result=filter_result,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return jsonify({
            "status": "success",
            "count": len(records),
            "data": records
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/students", methods=["POST"])
def add_student():
    """Adds a new student and recalculates metrics with Pandas."""
    try:
        payload = request.get_json(force=True)
        analyzer.add_student(payload)
        return jsonify({"status": "success", "message": "Student record added successfully."})
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route("/api/students/<reg_no>", methods=["GET"])
def get_single_student(reg_no):
    """Fetches full details for a single student mark sheet."""
    try:
        reg_no = str(reg_no).strip().upper()
        records = analyzer.get_student_records(search=reg_no)
        matched = [r for r in records if r["Register_No"].upper() == reg_no]
        if not matched:
            return jsonify({"status": "error", "message": "Student not found."}), 404
        return jsonify({"status": "success", "data": matched[0]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/students/<reg_no>", methods=["PUT"])
def update_student(reg_no):
    """Updates student marks and recalculates metrics."""
    try:
        payload = request.get_json(force=True)
        analyzer.update_student(reg_no, payload)
        return jsonify({"status": "success", "message": "Student record updated successfully."})
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route("/api/students/<reg_no>", methods=["DELETE"])
def delete_student(reg_no):
    """Deletes a student record."""
    try:
        analyzer.delete_student(reg_no)
        return jsonify({"status": "success", "message": "Student record deleted successfully."})
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route("/api/analysis/subjects", methods=["GET"])
def get_subject_analysis():
    """Returns Pandas-calculated subject performance metrics."""
    try:
        data = analyzer.get_subject_wise_analysis()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/analysis/class", methods=["GET"])
def get_class_analysis():
    """Returns Pandas class-wise statistical summary."""
    try:
        data = analyzer.get_class_wise_analysis()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- MATPLOTLIB CHARTS ----------------

@app.route("/api/charts/<chart_name>", methods=["GET"])
def get_chart(chart_name):
    """Generates and serves Matplotlib charts on-the-fly."""
    try:
        chart_name = chart_name.lower()
        if chart_name == "subject_averages":
            buf = analyzer.generate_chart_subject_averages()
        elif chart_name == "student_comparison":
            buf = analyzer.generate_chart_student_comparison()
        elif chart_name == "pass_fail_distribution":
            buf = analyzer.generate_chart_pass_fail_distribution()
        elif chart_name == "percentage_distribution":
            buf = analyzer.generate_chart_percentage_distribution()
        elif chart_name == "subject_comparison":
            buf = analyzer.generate_chart_subject_comparison()
        elif chart_name == "top_performers":
            buf = analyzer.generate_chart_top_performers()
        else:
            return jsonify({"status": "error", "message": f"Unknown chart type: {chart_name}"}), 404

        return send_file(buf, mimetype="image/png", as_attachment=False)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- CSV IMPORT & EXPORT ----------------

@app.route("/api/export-csv", methods=["GET"])
def export_csv():
    """Exports processed student result data with all calculated columns."""
    try:
        csv_data = analyzer.export_processed_csv()
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=SRM_CSE_K_Analyzed_Results.csv"}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/sample-csv", methods=["GET"])
def sample_csv():
    """Provides a sample CSV template for users to upload."""
    sample_content = (
        "Register_No,Student_Name,Department,Semester,Section,DSA_21CSC201J,OOP_21CSC202J,APP_21CSC203P,DM_21MTH201T,COA_21CSC204J\n"
        "RA2311003020050,Siddharth Raman,CSE,3,CSE/K,85,90,92,80,88\n"
        "RA2311003020051,Ananya Senthil,CSE,3,CSE/K,92,94,96,89,91\n"
        "RA2311003020052,Vijay Anand,CSE,3,CSE/K,74,78,82,69,75\n"
        "RA2311003020053,Kavya Murugan,CSE,3,CSE/K,48,55,60,45,52\n"
    )
    return Response(
        sample_content,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=SRM_Student_Result_Template.csv"}
    )

@app.route("/api/import-csv", methods=["POST"])
def import_csv():
    """Handles CSV file upload and processing with Pandas."""
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No CSV file uploaded."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Empty file name."}), 400

    mode = request.form.get("mode", "replace")  # 'replace' or 'append'

    try:
        count = analyzer.import_csv(file, mode=mode)
        return jsonify({
            "status": "success",
            "message": f"Successfully processed CSV. Dataset now contains {count} students."
        })
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to parse CSV: {str(e)}"}), 500

@app.route("/api/reset-data", methods=["POST"])
def reset_data():
    """Resets dataset to the initial 28 sample students."""
    try:
        if os.path.exists(BACKUP_CSV_PATH):
            import shutil
            shutil.copyfile(BACKUP_CSV_PATH, CSV_PATH)
            analyzer.load_data()
            return jsonify({"status": "success", "message": "Dataset successfully reset to original 28 sample records."})
        else:
            return jsonify({"status": "error", "message": "Backup dataset not found."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
