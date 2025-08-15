# src/models.py
from datetime import datetime, timedelta
from . import data_manager
from . import utils

class User:
    def __init__(self, user_id, name, role):
        self.user_id = user_id
        self.name = name
        self.role = role

    @staticmethod
    def login(user_id, password):
        """
        Authenticates a user.
        If successful, returns an instance of Student or Professor.
        Otherwise, returns None.
        """
        users = data_manager.get_users()
        for user_data in users:
            if user_data['id'] == user_id:
                if utils.verify_password(password, user_data['password_hash']):
                    if user_data['role'] == 'student':
                        return Student(user_id=user_data['id'], name=user_data['name'])
                    elif user_data['role'] == 'professor':
                        return Professor(user_id=user_data['id'], name=user_data['name'])
        return None

    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.user_id}', name='{self.name}')"


class Student(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name, 'student')

    def get_available_courses(self):
        """Returns a list of courses that have capacity."""
        all_courses = data_manager.get_courses()
        proposals = data_manager.get_proposals()
        available_courses = []

        for course in all_courses:
            approved_count = sum(1 for p in proposals if p['course_id'] == course['id'] and p['status'] == 'approved')
            if approved_count < course['capacity']:
                available_courses.append(course)

        return available_courses

    def submit_thesis_request(self, course_id):
        """Submits a new thesis proposal request."""
        proposals = data_manager.get_proposals()
        if any(p for p in proposals if p['student_id'] == self.user_id and p['status'] in ['pending', 'approved']):
            return False, "شما در حال حاضر یک درخواست فعال یا در انتظار تایید دارید."

        new_proposal = {
            "proposal_id": utils.generate_unique_id(), "student_id": self.user_id,
            "course_id": course_id, "request_date": utils.get_current_date_str(),
            "status": "pending", "approval_date": None
        }
        proposals.append(new_proposal)
        data_manager.save_proposals(proposals)
        return True, "درخواست شما با موفقیت ثبت و برای استاد ارسال شد."

    def view_my_thesis_status(self):
        """Retrieves the status of the student's thesis proposal."""
        proposals = data_manager.get_proposals()
        theses = data_manager.get_theses()

        my_proposal = next((p for p in proposals if p['student_id'] == self.user_id), None)
        if not my_proposal:
            return None, "no_proposal"

        course_info = next((c for c in data_manager.get_courses() if c['id'] == my_proposal['course_id']), None)

        my_thesis = next((t for t in theses if t.get('proposal_id') == my_proposal['proposal_id']), None)
        if my_thesis:
            return {"proposal": my_proposal, "course": course_info, "thesis": my_thesis}, "defense_status"

        return {"proposal": my_proposal, "course": course_info}, "proposal_status"


    def request_defense(self, title, abstract, keywords, pdf_path, image_path):
        """Submits a defense request if conditions are met."""
        proposals = data_manager.get_proposals()
        my_proposal = next((p for p in proposals if p['student_id'] == self.user_id and p['status'] == 'approved'), None)

        if not my_proposal:
            return False, "شما باید یک پروپوزال تایید شده داشته باشید."

        approval_date_str = my_proposal.get('approval_date')
        if not approval_date_str:
            return False, "تاریخ تایید پروپوزال شما ثبت نشده است."

        approval_date = datetime.strptime(approval_date_str, '%Y-%m-%d')
        if datetime.now() < approval_date + timedelta(days=90):
            return False, f"باید حداقل ۹۰ روز از تاریخ تایید پروپوزال شما ({approval_date_str}) گذشته باشد."

        theses = data_manager.get_theses()
        new_thesis = {
            "thesis_id": utils.generate_unique_id(),
            "proposal_id": my_proposal['proposal_id'],
            "title": title, "abstract": abstract, "keywords": keywords,
            "pdf_path": pdf_path, "cover_image_path": image_path,
            "status": "defense_pending", # defense_pending, defense_approved, defense_rejected, graded, defended
            "defense_request_date": utils.get_current_date_str(),
            "grades": {}, "reviewers": []
        }
        theses.append(new_thesis)
        data_manager.save_theses(theses)
        return True, "درخواست دفاع شما با موفقیت ثبت شد."


class Professor(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name, 'professor')
        self.supervision_limit = 5
        self.review_limit = 10

    def get_load(self):
        """Calculates current supervision and review load."""
        proposals = data_manager.get_proposals()
        theses = data_manager.get_theses()

        supervision_count = sum(1 for p in proposals if self.is_supervisor_for_proposal(p) and p['status'] == 'approved')
        review_count = sum(1 for t in theses if self.user_id in t.get('reviewers', []))

        return {"supervision": supervision_count, "review": review_count}

    def is_supervisor_for_proposal(self, proposal):
        course = next((c for c in data_manager.get_courses() if c['id'] == proposal['course_id']), None)
        return course and course['professor_id'] == self.user_id

    def get_pending_proposals(self):
        """Returns a list of pending thesis proposals for this professor."""
        proposals = data_manager.get_proposals()
        pending_list = []
        for p in proposals:
            if self.is_supervisor_for_proposal(p) and p['status'] == 'pending':
                student = next((u for u in data_manager.get_users() if u['id'] == p['student_id']), None)
                course = next((c for c in data_manager.get_courses() if c['id'] == p['course_id']), None)
                pending_list.append({"proposal": p, "student": student, "course": course})
        return pending_list

    def decide_on_proposal(self, proposal_id, decision):
        """Approves or rejects a thesis proposal."""
        if decision == 'approved' and self.get_load()['supervision'] >= self.supervision_limit:
            return False, "ظرفیت راهنمایی شما تکمیل است."

        proposals = data_manager.get_proposals()
        proposal_to_update = next((p for p in proposals if p['proposal_id'] == proposal_id and self.is_supervisor_for_proposal(p)), None)

        if not proposal_to_update:
            return False, "درخواست مورد نظر یافت نشد یا متعلق به شما نیست."

        proposal_to_update['status'] = decision
        if decision == 'approved':
            proposal_to_update['approval_date'] = utils.get_current_date_str()
            # Reject other pending proposals from the same student
            for p in proposals:
                if p['student_id'] == proposal_to_update['student_id'] and p['status'] == 'pending':
                    p['status'] = 'rejected'

        data_manager.save_proposals(proposals)
        return True, f"درخواست با موفقیت {decision} شد."

    def get_pending_defense_requests(self):
        """Returns defense requests for theses supervised by this professor."""
        theses = data_manager.get_theses()
        proposals = data_manager.get_proposals()
        users = data_manager.get_users()

        pending_list = []
        for thesis in theses:
            if thesis['status'] == 'defense_pending':
                proposal = next((p for p in proposals if p.get('proposal_id') == thesis.get('proposal_id')), None)
                if proposal and self.is_supervisor_for_proposal(proposal):
                    student = next((u for u in users if u['id'] == proposal['student_id']), None)
                    pending_list.append({'thesis': thesis, 'student': student})
        return pending_list

    def decide_on_defense(self, thesis_id, decision, defense_date, reviewer_ids):
        """Approves or rejects a defense request."""
        theses = data_manager.get_theses()
        thesis_to_update = next((t for t in theses if t['thesis_id'] == thesis_id), None)

        if not thesis_to_update:
            return False, "پایان‌نامه یافت نشد."

        if decision == 'approved':
            thesis_to_update['status'] = 'defense_approved'
            thesis_to_update['defense_date'] = defense_date
            thesis_to_update['reviewers'] = reviewer_ids
        else:
            thesis_to_update['status'] = 'defense_rejected'

        data_manager.save_theses(theses)
        return True, f"درخواست دفاع با موفقیت {decision} شد."

    def get_theses_to_review(self):
        """Returns theses assigned to this professor for review."""
        theses = data_manager.get_theses()
        proposals = data_manager.get_proposals()
        users = data_manager.get_users()
        review_list = []
        for thesis in theses:
            if self.user_id in thesis.get('reviewers', []) and thesis.get('status') == 'defense_approved':
                proposal = next((p for p in proposals if p.get('proposal_id') == thesis.get('proposal_id')), None)
                student = next((u for u in users if u['id'] == proposal['student_id']), None)
                review_list.append({'thesis': thesis, 'student': student})
        return review_list

    def submit_grade(self, thesis_id, grade):
        """Submits a grade for a thesis."""
        theses = data_manager.get_theses()
        thesis = next((t for t in theses if t['thesis_id'] == thesis_id), None)
        if not thesis:
            return False, "پایان‌نامه یافت نشد."

        # Check if today is after the defense date
        defense_date = datetime.strptime(thesis['defense_date'], '%Y-%m-%d')
        if datetime.now() < defense_date:
            return False, "هنوز تاریخ دفاع فرا نرسیده است."

        # Record grade
        thesis['grades'][self.user_id] = grade

        # Check if all grades are submitted
        supervisor_id = next(c['professor_id'] for c in data_manager.get_courses() if c['id'] == next(p['course_id'] for p in data_manager.get_proposals() if p['proposal_id'] == thesis['proposal_id']))
        all_graders = thesis['reviewers'] + [supervisor_id]

        if all(g_id in thesis['grades'] for g_id in all_graders):
            thesis['status'] = 'graded'

        data_manager.save_theses(theses)
        return True, "نمره با موفقیت ثبت شد."

    def generate_performance_report(self):
        """Generates a performance report for the professor."""
        theses = data_manager.get_theses()
        proposals = data_manager.get_proposals()

        supervised_count = 0
        reviewed_count = 0
        supervised_student_grades = []

        for thesis in [t for t in theses if t.get('status') in ['graded', 'defended']]:
            # Check for supervision
            proposal = next((p for p in proposals if p['proposal_id'] == thesis['proposal_id']), None)
            if proposal and self.is_supervisor_for_proposal(proposal):
                supervised_count += 1
                total_score = sum(thesis['grades'].values())
                avg_score = total_score / len(thesis['grades']) if thesis['grades'] else 0
                student = next((u for u in data_manager.get_users() if u['id'] == proposal['student_id']), None)
                supervised_student_grades.append({
                    "student_name": student['name'] if student else 'N/A',
                    "thesis_title": thesis['title'],
                    "final_grade": f"{avg_score:.2f}"
                })

            # Check for reviewing
            if self.user_id in thesis.get('reviewers', []):
                reviewed_count += 1

        return {
            "supervised_theses_count": supervised_count,
            "reviewed_theses_count": reviewed_count,
            "supervised_students": supervised_student_grades
        }

def get_letter_grade(score):
    """Converts a numerical score (0-20) to a letter grade."""
    if 17 <= score <= 20:
        return "الف"
    elif 13 <= score < 17:
        return "ب"
    elif 10 <= score < 13:
        return "ج"
    else:
        return "د"

def search_theses_archive(query, search_by="title"):
    """
    Searches the archive of defended theses.
    'search_by' can be 'title', 'keyword', 'author', 'supervisor', 'reviewer', 'year'.
    """
    theses = data_manager.get_theses()
    proposals = data_manager.get_proposals()
    users = data_manager.get_users()
    courses = data_manager.get_courses()

    # Filter for defended theses only
    defended_theses = [t for t in theses if t.get('status') in ['graded', 'defended']]

    results = []
    for thesis in defended_theses:
        proposal = next((p for p in proposals if p['proposal_id'] == thesis['proposal_id']), None)
        if not proposal: continue

        student = next((u for u in users if u['id'] == proposal['student_id']), None)
        course = next((c for c in courses if c['id'] == proposal['course_id']), None)
        supervisor = next((u for u in users if u['id'] == course['professor_id']), None)
        reviewers = [next((u for u in users if u['id'] == r_id), None) for r_id in thesis['reviewers']]

        # Match query against the specified field
        match = False
        if search_by == 'title' and query.lower() in thesis['title'].lower():
            match = True
        elif search_by == 'keyword' and query.lower() in thesis['keywords'].lower():
            match = True
        elif search_by == 'author' and query.lower() in student['name'].lower():
            match = True
        elif search_by == 'supervisor' and query.lower() in supervisor['name'].lower():
            match = True
        elif search_by == 'year' and query == str(course['year']):
            match = True
        elif search_by == 'reviewer' and any(query.lower() in r['name'].lower() for r in reviewers if r):
            match = True

        if match:
            total_score = sum(thesis['grades'].values())
            avg_score = total_score / len(thesis['grades']) if thesis['grades'] else 0

            results.append({
                "title": thesis['title'],
                "abstract": thesis['abstract'],
                "keywords": thesis['keywords'],
                "author": student['name'],
                "year": course['year'],
                "semester": course['semester'],
                "supervisor": supervisor['name'],
                "reviewers": [r['name'] for r in reviewers if r],
                "download_link": thesis['pdf_path'],
                "final_grade_score": f"{avg_score:.2f}",
                "final_grade_letter": get_letter_grade(avg_score)
            })

    return results
