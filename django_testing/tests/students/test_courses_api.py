import pytest
from rest_framework.test import APIClient

from students.models import Course

from students.models import Student
from model_bakery import baker


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_factory():
    def create_student(**kwargs):
        return baker.make(Student, **kwargs)
    return create_student


@pytest.fixture
def course_factory(student_factory):
    def create_course(**kwargs):
        students = kwargs.pop('students', [])
        course = baker.make(Course, **kwargs)

        if students:
            course.students.set(students)

        return course
    return create_course



@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory): # создаем курс с помощью фабрики

    course = course_factory(name="Test Course")
    url = f'/api/v1/courses/{course.id}/'
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['id'] == course.id
    assert response.data['name'] == course.name

@pytest.mark.django_db
def test_list_courses(api_client, course_factory): #Несколько курсов

    courses = course_factory(_quantity=3)

    url = '/api/v1/courses/'
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 3
    for i in range(len(courses)):
        assert response.data[i]['id'] == courses[i].id
        assert response.data[i]['name'] == courses[i].name



@pytest.mark.django_db
def test_filter_by_id(api_client, course_factory):

    courses = course_factory(_quantity=3)
    url = f'/api/v1/courses/?id={courses[0].id}'
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['id'] == courses[0].id
    assert response.data[0]['name'] == courses[0].name



@pytest.mark.django_db
def test_filter_by_name(api_client, course_factory):

    course1 = course_factory(name="Python Basics")
    course2 = course_factory(name="Django Advanced")
    course3 = course_factory(name="React Fundamentals")

    url = '/api/v1/courses/?name=Django+Advanced'
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['id'] == course2.id
    assert response.data[0]['name'] == 'Django Advanced'

@pytest.mark.django_db
def test_create_course(api_client): #JSON данные
    data = {
        'name': 'New Course',
    }

    url = '/api/v1/courses/'
    response = api_client.post(url, data, format='json')

    assert response.status_code == 201
    assert response.data['name'] == 'New Course'


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    course = course_factory(name='Old Name')
    data = {
        'name': 'Updated Name',
    }

    url = f'/api/v1/courses/{course.id}/'
    response = api_client.put(url, data, format='json')

    assert response.status_code == 200
    assert response.data['name'] == 'Updated Name'


@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    course = course_factory()

    url = f'/api/v1/courses/{course.id}/'
    response = api_client.delete(url)

    assert response.status_code == 204

    url = f'/api/v1/courses/{course.id}/'
    response = api_client.get(url)
    assert response.status_code == 404

