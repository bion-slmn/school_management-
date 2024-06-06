from django.shortcuts import render, redirect 
from django.http import HttpResponse, HttpResponseRedirect 
from django.contrib import messages 
from django.core.files.storage import FileSystemStorage 
from django.urls import reverse 
import datetime
from .models import (
    CustomUser, Staffs, Courses,
    Subjects, Students, Attendance,
    AttendanceReport, LeaveReportStudent, FeedBackStudent,
    StudentResult 
)
from django.db.models import Q

def student_home(request: HttpRequest) ->HttpResponse:
    student_obj = Students.objects.select_related(
        'course_id'
        ).get(admin=request.user.id)

    attendance_data = AttendanceReport.objects.filter(student_id=student_obj).aggregate(
        total_attendance=Count('id'),
        attendance_present=Count('id', filter=Q(status=True)),
        attendance_absent=Count('id', filter=Q(status=False)),
    )

    total_subjects = Subjects.objects.filter(
        course_id=student_obj.course_id
        ).count()
    
    subject_name = [] 
    data_present = [] 
    data_absent = [] 
    subject_data = Subjects.objects.filter(course_id=student_obj.course_id) 
    for subject in subject_data: 
        attendance = Attendance.objects.filter(subject_id=subject.id) 
        attendance_present_count = AttendanceReport.objects.filter(
            attendance_id__in=attendance, 
            status=True, 
            student_id=student_obj.id
            ).count() 
        attendance_absent_count = AttendanceReport.objects.filter(
            attendance_id__in=attendance, 
            status=False, 
            student_id=student_obj.id
            ).count() 
        subject_name.append(subject.subject_name) 
        data_present.append(attendance_present_count) 
        data_absent.append(attendance_absent_count)

    return render(request, "student_template/student_home_template.html")


def student_view_attendance_post(request: HttpRequest) ->HttpResponse:
    student = Student.objects.get(request.user.id)

    course = student.course_id

    subject = subject.objects.filter(course_id=course)

    context = {'subjects': subject}
    return render(request, "student_template/student_view_attendance.html", context) 
  

def student_view_attendance_post(request: HttpRequest) ->HttpResponse: 
    if request.method != 'POST':
        messages.error(request, "Invalid Method") 
        return redirect('student_view_attendance')

    subject_id = request.POST.get('subject') 
    start_date = request.POST.get('start_date') 
    end_date = request.POST.get('end_date')

    start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date() 
    end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date() 

    subject_object = Subjects.objects.get(id=subject_id)
    user_obj = CustomUser.objects.get(id=request.user.id)
    stud_obj = Student.objects.get(admin=user_obj)

    attendance = Attendance.objects.filter(
        attendance_date__range=(start_date_parse,
                               end_date_parse),
        subject_id=subject_object
    )

    attendance_reports = AttendanceReport.objects.filter(
        attendance_id__in=attendance,
        student_id=stud_obj
    )

    context = {
        'subject_obj': subject_object,
        "attendance_reports": attendance_reports 
    }

    return render(
        request,
        'student_template/student_attendance_data.html',
        context,
        ) 


def student_apply_leave(request): 
    student_obj = Students.objects.prefetch_related(
        'leavereportstudent'
    ).get(admin=request.user.id) 
    
    context = { 
        "leave_data": student_obj.leavereportstudent_set.all()
    } 
    return render(request, 'student_template/student_apply_leave.html', context) 
  

def student_apply_leave_save(request): 
    if request.method != 'POST':
        messages.error(request, "Invalid Method") 
        return redirect('student_apply_leave')

    leave_date = request.POST.get('leave_date')
    leave_message = request.POST.get('leave_message')

    student_obj = Students.objects.get(admin=request.user.id)

    try:
        leave_report = LeaveReportStudent.objects.create(student_id=student_obj,
                                          leave_data=leave_data,
                                          leave_message=leave_message,
                                          leave_status=0)
        messages.success(request, "Applied for Leave.") 
        return redirect('student_apply_leave') 
    except Exception: 
        messages.error(request, "Failed to Apply Leave") 
        return redirect('student_apply_leave')
                    

def student_feedback(request): 
    student_obj = Students.objects.prefetch_related(
        'feedbackstudent'
        ).get(admin=request.user.id) 
    
    context = { 
        "feedback_data": student_obj.feedbackstudent_set.all()
    } 
    return render(request, 'student_template/student_feedback.html', context) 
  
  
def student_feedback_save(request): 
    if request.method != "POST": 
        messages.error(request, "Invalid Method.") 
        return redirect('student_feedback') 
     
    feedback = request.POST.get('feedback_message') 
    student_obj = Students.objects.get(admin=request.user.id) 
  
    try: 
        add_feedback = FeedBackStudent(student_id=student_obj, 
                                        feedback=feedback, 
                                        feedback_reply="") 
        add_feedback.save() 
        messages.success(request, "Feedback Sent.") 
        return redirect('student_feedback') 
    except Exception: 
        messages.error(request, "Failed to Send Feedback.") 
        return redirect('student_feedback') 
  
  
def student_profile(request): 
    user = CustomUser.objects.select_related(
        'student'
        ).get(id=request.user.id)  
  
    context={ 
        "user": user, 
        "student": user.student 
    } 
    return render(request, 'student_template/student_profile.html', context) 
  
  
def student_profile_update(request): 
    if request.method != "POST": 
        messages.error(request, "Invalid Method!") 
        return redirect('student_profile')
    
    attributes = ['first_name', 'last_name', 'password', 'address']
    student_data = {attr: request.POST.get(attr) for attr in attributes}

    try: 
        save_student_data(request, student_data)
        messages.success(request, "Profile Updated Successfully")
        return redirect('student_profile')
    except Exception: 
        messages.error(request, "Failed to Update Profile") 
        return redirect('student_profile') 

def save_student_data(request, student_data: Dict[str, str]) ->None:
    customuser = CustomUser.objects.get(id=request.user.id)
    customuser.first_name = student_data.get('first_name')
    customuser.last_name = student_data.get('last_name')
    
    password = student_data.get('password')
    if password not in [None, ""]: 
            customuser.set_password(password)
    customuser.save() 

    student = Students.objects.get(admin=customuser.id)
    student.address = student_data.get('address')
    student.save() 
  
  
def student_view_result(request): 

    student = Student.objects.prefetch_related(
        'studentresult'
        ).get(admin=request.user.id)
    
    context = { 
        "student_result": student.studentresult_set.all(), 
    } 
    return render(request, "student_template/student_view_result.html", context)