from django.contrib.auth.models import AbstractUser 
from django.db import models 
from django.db.models.signals import post_save 
from django.dispatch import receiver
import uuid


class SemisterModel(models.Model):
    '''
    defines a semister or term in a year
    '''
    id = models.UUIDField(
        primary_key=True,
        default = uuid.uuid4,
        editable = False
    )
    semister_starts = models.DateField()
    semister_ends = models.DateField()


class CustomUser(AbstractUser):
    '''
    adds fiels to the django user objects
    '''
    HOD = '1'
    STAFF = '2'
    STUDENT = '3'
      
    EMAIL_TO_USER_TYPE_MAP = { 
        'hod': HOD, 
        'staff': STAFF, 
        'student': STUDENT 
    } 
  
    user_type_data = ((HOD, "HOD"), (STAFF, "Staff"), (STUDENT, "Student")) 
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10) 



class BaseModel(models.Model):
    '''
    create a base class to inherit attributes,
    '''
    id = models.UUIDField(
        primary_key=True,
        default = uuid.uuid4,
        editable = False
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True

class AdminHOD(BaseModel):
    '''
    defines the admin class, and inherits from base class
    '''
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)


class Staffs(BaseModel):
    '''
    defines the attribes of a staff object
    ''' 
    admin = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    address = models.TextField()


class Courses(BaseModel):
    '''
    defines the attributes of a course or subject
    '''
    course_name = models.CharField(max_length=255)

class Subjects(BaseModel):
    '''
    defines the subjects that are in a course
    '''
    subject_name = models.CharField(max_length=255) 
    course_id = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE
        )  
    staff_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Students(BaseModel):
    '''
    Defines a model for a student object
    '''
    admin = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )
    gender = models.CharField(max_length=50)
    profile_pic = models.FileField()
    address = models.TextField()
    course_id = models.ForeignKey(Courses, on_delete=models.DO_NOTHING)
    semister_year_id = models.ForeignKey(
        SemisterModel,
        null=True,
        on_delete=models.CASCADE
    )

class Attendance(BaseModel):
    '''
    defines a model for student attendance
    '''
    subject_id = models.ForeignKey(
        Subjects,
        on_delete=models.DO_NOTHING
    )
    attendance_date = models.DateField()
    semister_year_id = models.ForeignKey(
        SemisterModel,
        on_delete=models.CASCADE
    )
    
class AttendanceReport(BaseModel):
    '''
    Define a model attendance report
    '''
    student_id = models.ForeignKey(
        Students,
        on_delete=models.DO_NOTHING
        ) 
    attendance_id = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE
        ) 
    status = models.BooleanField(default=False) 


class LeaveReportStudent(BaseModel):
    '''
    Define a leave report for students
    '''
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE) 
    leave_date = models.CharField(max_length=255) 
    leave_message = models.TextField() 
    leave_status = models.IntegerField(default=0)


class LeaveReportStaff(BaseModel):
    '''
    Define a leave report for staff
    '''
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE) 
    leave_date = models.CharField(max_length=255) 
    leave_message = models.TextField() 
    leave_status = models.IntegerField(default=0)

class FeedBackStudent(BaseModel):
    '''
    define a feed back model
    '''
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE) 
    feedback = models.TextField() 
    feedback_reply = models.TextField()

class FeedBackStaffs(BaseModel):
    '''
    define a feed back model for students
    '''
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE) 
    feedback = models.TextField() 
    feedback_reply = models.TextField()


class NotificationStudent(BaseModel):
    '''
    defining model for notifications
    '''
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE) 
    message = models.TextField()


class NotificationStaffs(BaseModel):
    '''
    defining model for notification for students
    '''
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE) 
    message = models.TextField()

class StudentResult(BaseModel):
    '''
    defining results for students
    '''
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE) 
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE) 
    subject_exam_marks = models.FloatField(default=0) 
    subject_assignment_marks = models.FloatField(default=0) 