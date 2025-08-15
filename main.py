# main.py - Entry point for the Thesis Management System CLI
import os
import getpass
from src import models

# Global variable to hold the logged-in user object
current_user = None

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Prints a formatted header."""
    print("=" * 40)
    print(f"{title:^40}")
    print("=" * 40)

def handle_list_available_courses(student):
    """Handles listing available courses for a student."""
    print_header("دروس پایان‌نامه قابل اخذ")
    courses = student.get_available_courses()
    if not courses:
        print("در حال حاضر هیچ درس پایان‌نامه‌ای با ظرفیت خالی وجود ندارد.")
    else:
        print(f"{'ID':<10} {'عنوان':<30} {'استاد':<20} {'ظرفیت باقی‌مانده'}")
        print("-" * 80)
        professors = models.data_manager.get_users()
        proposals = models.data_manager.get_proposals()

        for course in courses:
            prof_name = next((p['name'] for p in professors if p['id'] == course['professor_id']), 'N/A')
            approved_count = sum(1 for p in proposals if p['course_id'] == course['id'] and p['status'] == 'approved')
            remaining_capacity = course['capacity'] - approved_count
            print(f"{course['id']:<10} {course['title']:<30} {prof_name:<20} {remaining_capacity}")
    input("\nبرای بازگشت به منو، Enter را فشار دهید...")

def handle_submit_request(student):
    """Handles submitting a thesis request."""
    print_header("ثبت درخواست اخذ پایان‌نامه")
    courses = student.get_available_courses()
    if not courses:
        print("در حال حاضر درسی برای اخذ وجود ندارد.")
        input("\nبرای بازگشت به منو، Enter را فشار دهید...")
        return

    print("لیست دروس قابل اخذ:")
    for course in courses:
        print(f"  - ID: {course['id']}, عنوان: {course['title']}")

    course_id = input("لطفا ID درس مورد نظر را وارد کنید: ").strip()

    if any(c['id'] == course_id for c in courses):
        success, message = student.submit_thesis_request(course_id)
        print(message)
    else:
        print("ID وارد شده نامعتبر است.")

    input("\nبرای بازگشت به منو، Enter را فشار دهید...")

def handle_view_status(student):
    """Handles viewing the status of a student's request."""
    print_header("مشاهده وضعیت درخواست")
    result, status_type = student.view_my_thesis_status()

    if status_type == "no_proposal":
        print("شما هیچ درخواست ثبت‌شده‌ای ندارید.")
    elif status_type == "proposal_status":
        status_map = {"pending": "در انتظار تأیید استاد", "approved": "تأیید شده", "rejected": "رد شده"}
        proposal = result['proposal']
        course = result['course']
        print(f"وضعیت درخواست پروپوزال شما برای درس '{course['title']}'")
        print(f"تاریخ درخواست: {proposal['request_date']}")
        print(f"وضعیت: {status_map.get(proposal['status'], 'نامشخص')}")
        if proposal['status'] == 'approved':
             print(f"تاریخ تایید: {proposal['approval_date']}")
    elif status_type == "defense_status":
        status_map = {
            "defense_pending": "درخواست دفاع ثبت شده، در انتظار تایید استاد راهنما",
            "defense_rejected": "درخواست دفاع رد شده",
            "defense_approved": "دفاع تایید شده، منتظر برگزاری جلسه",
            "graded": "نمره‌دهی شده",
            "defended": "دفاع شده و مختومه"
        }
        thesis = result['thesis']
        print(f"وضعیت پایان‌نامه شما: '{thesis['title']}'")
        print(f"وضعیت فعلی: {status_map.get(thesis['status'], 'نامشخص')}")
        if thesis.get('defense_date'):
            print(f"تاریخ دفاع: {thesis['defense_date']}")

    input("\nبرای بازگشت به منو، Enter را فشار دهید...")

def handle_request_defense(student):
    """Handles the process of requesting a defense session."""
    print_header("ثبت درخواست دفاع")
    print("برای ثبت درخواست دفاع، لطفا اطلاعات زیر را تکمیل کنید:")
    title = input("عنوان کامل پایان‌نامه: ")
    abstract = input("چکیده: ")
    keywords = input("کلمات کلیدی (با کاما جدا کنید): ")
    pdf_path = input("مسیر فایل PDF پایان‌نامه: ")
    image_path = input("مسیر فایل تصویر صفحه اول: ")

    success, message = student.request_defense(title, abstract, keywords, pdf_path, image_path)
    print(f"\n{message}")
    input("\nبرای بازگشت به منو، Enter را فشار دهید...")


def student_dashboard(student):
    """Displays the student's main menu and handles their actions."""
    global current_user
    while True:
        clear_screen()
        print_header(f"داشبورد دانشجو - {student.name} خوش آمدید")
        print("1. مشاهده دروس پایان‌نامه قابل اخذ")
        print("2. ثبت درخواست اخذ پایان‌نامه")
        print("3. مشاهده وضعیت درخواست")

        # Check if student is eligible for defense request
        is_eligible_for_defense = False
        result, status_type = student.view_my_thesis_status()
        if status_type == 'proposal_status' and result['proposal']['status'] == 'approved':
             approval_date = models.datetime.strptime(result['proposal']['approval_date'], '%Y-%m-%d')
             if models.datetime.now() >= approval_date + models.timedelta(days=90):
                 is_eligible_for_defense = True

        if is_eligible_for_defense:
            print("4. ثبت درخواست دفاع")
        print("5. جستجو در آرشیو پایان‌نامه‌ها")
        print("6. خروج (Logout)")

        choice = input("\nلطفا گزینه مورد نظر را انتخاب کنید: ")

        if choice == '1':
            handle_list_available_courses(student)
        elif choice == '2':
            handle_submit_request(student)
        elif choice == '3':
            handle_view_status(student)
        elif choice == '4' and is_eligible_for_defense:
            handle_request_defense(student)
        elif choice == '5':
            handle_search_archive()
        elif choice == '6':
            current_user = None
            print("با موفقیت خارج شدید.")
            break
        else:
            print("انتخاب نامعتبر است. لطفا دوباره تلاش کنید.")
            input("برای ادامه Enter را فشار دهید...")


def handle_manage_proposals(professor):
    """Handles viewing and deciding on thesis proposals."""
    print_header("مدیریت درخواست‌های اخذ پایان‌نامه")
    pending_proposals = professor.get_pending_proposals()

    if not pending_proposals:
        print("هیچ درخواست در حال انتظاری برای شما وجود ندارد.")
        input("\nبرای بازگشت به منو، Enter را فشار دهید...")
        return

    print(f"{'ID درخواست':<10} {'نام دانشجو':<20} {'عنوان درس'}")
    print("-" * 60)
    for item in pending_proposals:
        proposal = item['proposal']
        student = item['student']
        course = item['course']
        print(f"{proposal['proposal_id']:<10} {student['name']:<20} {course['title']}")

    print("\nبرای تایید یا رد یک درخواست، ID آن را وارد کنید (یا برای بازگشت Enter بزنید):")
    proposal_id = input("> ").strip()

    if not proposal_id: return
    if not any(item['proposal']['proposal_id'] == proposal_id for item in pending_proposals):
        print("ID درخواست نامعتبر است.")
        input("\nبرای بازگشت به منو، Enter را فشار دهید..."); return

    decision = input("تصمیم خود را وارد کنید (approve / reject): ").strip().lower()
    if decision in ['approve', 'reject']:
        success, message = professor.decide_on_proposal(proposal_id, decision)
        print(message)
    else:
        print("دستور نامعتبر است.")

    input("\nبرای بازگشت به منو، Enter را فشار دهید...")

def handle_manage_defense_requests(professor):
    """Handles approving/rejecting defense requests."""
    print_header("مدیریت درخواست‌های دفاع")
    requests = professor.get_pending_defense_requests()
    if not requests:
        print("هیچ درخواست دفاع در حال انتظاری وجود ندارد.")
        input("\nبرای بازگشت به منو، Enter را فشار دهید..."); return

    print(f"{'ID پایان‌نامه':<10} {'نام دانشجو':<20} {'عنوان'}")
    print("-" * 70)
    for req in requests:
        print(f"{req['thesis']['thesis_id']:<10} {req['student']['name']:<20} {req['thesis']['title']}")

    thesis_id = input("\nID پایان‌نامه برای مدیریت را وارد کنید: ").strip()
    if not any(r['thesis']['thesis_id'] == thesis_id for r in requests):
        print("ID نامعتبر است."); input("\nEnter..."); return

    decision = input("تصمیم خود را وارد کنید (approve / reject): ").strip().lower()
    if decision == 'approve':
        date = input("تاریخ دفاع (YYYY-MM-DD): ")

        all_profs = [u for u in models.data_manager.get_users() if u['role'] == 'professor' and u['id'] != professor.user_id]
        print("\nاساتید موجود برای داوری:")
        for p in all_profs: print(f"  - ID: {p['id']}, نام: {p['name']}")

        r1_id = input("ID داور داخلی: ")
        r2_id = input("ID داور خارجی: ")

        success, message = professor.decide_on_defense(thesis_id, 'approved', date, [r1_id, r2_id])
        print(message)

    elif decision == 'reject':
        success, message = professor.decide_on_defense(thesis_id, 'rejected', None, None)
        print(message)
    else:
        print("تصمیم نامعتبر.")

    input("\nبرای بازگشت به منو، Enter را فشار دهید...")

def handle_submit_grade(professor):
    """Handles submitting grades for reviewed theses."""
    print_header("ثبت نمره پایان‌نامه")
    theses_to_review = professor.get_theses_to_review()
    if not theses_to_review:
        print("پایان‌نامه‌ای برای نمره‌دهی به شما تخصیص داده نشده است.")
        input("\nبرای بازگشت به منو، Enter را فشار دهید..."); return

    print(f"{'ID پایان‌نامه':<10} {'نام دانشجو':<20} {'عنوان'}")
    print("-" * 70)
    for item in theses_to_review:
        print(f"{item['thesis']['thesis_id']:<10} {item['student']['name']:<20} {item['thesis']['title']}")

    thesis_id = input("\nID پایان‌نامه برای نمره‌دهی را وارد کنید: ").strip()
    if not any(t['thesis']['thesis_id'] == thesis_id for t in theses_to_review):
        print("ID نامعتبر است."); input("\nEnter..."); return

    try:
        grade = float(input("نمره (0-20): "))
        if not 0 <= grade <= 20: raise ValueError
        success, message = professor.submit_grade(thesis_id, grade)
        print(message)
    except ValueError:
        print("نمره باید یک عدد بین 0 و 20 باشد.")

    input("\nبرای بازگشت به منو، Enter را فشار دهید...")

def handle_performance_report(professor):
    """Generates and displays a professor's performance report."""
    print_header("گزارش عملکرد")
    report = professor.generate_performance_report()

    print(f"تعداد کل پایان‌نامه‌های راهنمایی شده: {report['supervised_theses_count']}")
    print(f"تعداد کل داوری‌های انجام شده: {report['reviewed_theses_count']}")

    print("\nلیست دانشجویان راهنمایی شده و نمرات نهایی:")
    print("-" * 50)
    if not report['supervised_students']:
        print("موردی یافت نشد.")
    else:
        for student_info in report['supervised_students']:
            print(f"  دانشجو: {student_info['student_name']}")
            print(f"  عنوان: {student_info['thesis_title']}")
            print(f"  نمره: {student_info['final_grade']}\n")

    input("\nبرای بازگشت، Enter را فشار دهید...")

def handle_search_archive():
    """Handles searching the thesis archive."""
    print_header("جستجو در آرشیو پایان‌نامه‌ها")
    print("جستجو بر اساس:")
    print("1. عنوان (title)")
    print("2. کلمه کلیدی (keyword)")
    print("3. نویسنده (author)")
    print("4. استاد راهنما (supervisor)")
    print("5. سال (year)")

    choice = input("گزینه مورد نظر را انتخاب کنید: ")
    search_by_map = {'1': 'title', '2': 'keyword', '3': 'author', '4': 'supervisor', '5': 'year'}

    if choice not in search_by_map:
        print("گزینه نامعتبر."); input("\nEnter..."); return

    search_by = search_by_map[choice]
    query = input(f"عبارت مورد نظر برای جستجو در '{search_by}' را وارد کنید: ").strip()

    results = models.search_theses_archive(query, search_by)

    clear_screen()
    print_header(f"نتایج جستجو برای '{query}'")
    if not results:
        print("هیچ نتیجه‌ای یافت نشد.")
    else:
        for i, res in enumerate(results, 1):
            print(f"--- نتیجه {i} ---")
            print(f"عنوان: {res['title']}")
            print(f"نویسنده: {res['author']} | سال: {res['year']}")
            print(f"استاد راهنما: {res['supervisor']}")
            print(f"داوران: {', '.join(res['reviewers'])}")
            print(f"کلمات کلیدی: {res['keywords']}")
            print(f"چکیده: {res['abstract'][:100]}...")
            print(f"لینک دانلود: {res['download_link']}")
            print(f"نمره نهایی: {res['final_grade_letter']} ({res['final_grade_score']})")
            print("-" * 20)

    input("\nبرای بازگشت، Enter را فشار دهید...")

def professor_dashboard(professor):
    """Displays the professor's main menu and handles their actions."""
    global current_user
    while True:
        clear_screen()
        load = professor.get_load()
        print_header(f"داشبورد استاد - {professor.name} خوش آمدید")
        print(f"ظرفیت راهنمایی: {load['supervision']}/{professor.supervision_limit} | ظرفیت داوری: {load['review']}/{professor.review_limit}")
        print("1. مدیریت درخواست‌های اخذ پایان‌نامه")
        print("2. مدیریت درخواست‌های دفاع")
        print("3. ثبت نمره به عنوان داور")
        print("4. جستجو در آرشیو پایان‌نامه‌ها")
        print("5. مشاهده گزارش عملکرد")
        print("6. خروج (Logout)")

        choice = input("\nلطفا گزینه مورد نظر را انتخاب کنید: ")

        if choice == '1':
            handle_manage_proposals(professor)
        elif choice == '2':
            handle_manage_defense_requests(professor)
        elif choice == '3':
            handle_submit_grade(professor)
        elif choice == '4':
            handle_search_archive()
        elif choice == '5':
            handle_performance_report(professor)
        elif choice == '6':
            current_user = None
            print("با موفقیت خارج شدید.")
            break
        else:
            print("انتخاب نامعتبر است. لطفا دوباره تلاش کنید.")
            input("برای ادامه Enter را فشار دهید...")

def main():
    """
    Main function to run the command-line interface.
    Handles user login and navigation.
    """
    global current_user
    while True:
        clear_screen()
        print_header("سیستم مدیریت پایان‌نامه‌ها")
        if not current_user:
            print("لطفا برای ورود، اطلاعات خود را وارد کنید یا برای خروج 'exit' را تایپ کنید.")
            user_id = input("کد کاربری: ")
            if user_id.lower() == 'exit':
                break

            password = getpass.getpass("رمز عبور: ")

            user = models.User.login(user_id, password)
            if user:
                current_user = user
                print("ورود موفقیت‌آمیز بود!")
                input("برای ادامه Enter را فشار دهید...")
            else:
                print("کد کاربری یا رمز عبور نامعتبر است.")
                input("برای تلاش مجدد Enter را فشار دهید...")

        if current_user:
            if current_user.role == 'student':
                student_dashboard(current_user)
            elif current_user.role == 'professor':
                professor_dashboard(current_user)

if __name__ == "__main__":
    main()
