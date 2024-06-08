from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions 
import datetime
from .models import (
    CustomUser, Staffs, Courses,
    Subjects, Students, Attendance,
    AttendanceReport, LeaveReportStudent, FeedBackStudent,
    StudentResult
)
from .serialiser import StudentSerialiser, CustomUserSerializer
from django.db.models import Q
from typing import Dict
from django.http import HttpRequest, HttpResponse
from rest_framework.permissions import IsAuthenticated


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
  
class StudentProfile(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs) ->Response:
        user = CustomUser.objects.filter(id=request.user.id).first()
        data = CustomUserSerializer(user).data
        return Response(data)

    def put(self, request, *args, **kwargs) ->Response:
        student_data = request.data
 
        customuser = CustomUser.objects.get(id=request.user.id)
        serializer = CustomUserSerializer(customuser, data=student_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            student = Students.objects.get(admin=customuser.id)
            student.address = student_data.get('address')
            student.save()
            return Response(serializer.data, 201)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

def save_student_data(request, student_data: Dict[str, str]) ->None:
    """
    Updates the student data in the database based on the
        provided student_data dictionary.

    Args:
        request: The HTTP request object.
        student_data: A dictionary containing student data attributes
                        to be updated.

    Returns:
        None
    """

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
    """
    Renders the page for a student to view their academic results.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse object containing the rendered academic
                    results view template.
    """


    student = Student.objects.prefetch_related(
        'studentresult'
        ).get(admin=request.user.id)
    
    context = { 
        "student_result": student.studentresult_set.all(), 
    } 
    return render(request, "student_template/student_view_result.html", context)