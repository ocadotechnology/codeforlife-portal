from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation_directly, join_teacher_to_organisation
from utils.classes import create_class, create_class_directly, transfer_class
from utils.student import create_school_student_directly
from utils.messages import is_class_created_message_showing, is_class_nonempty_message_showing

class TestClass(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).goToTeachPage().login(email, password).goToClassesPage()

        assert not page.have_classes()
        
        page, class_name, access_code = create_class(page)
        assert is_class_created_message_showing(self.browser, class_name)

        page = page.goToClassesPage()
        assert page.have_classes()
        assert page.does_class_exist(class_name, access_code)

        page = page.goToClassPage(class_name)
        assert not page.have_students()

        page = page.goToClassSettingsPage()
        assert page.checkClassDetails({
            'name': class_name,
            'classmates_data_viewable': False,
        })

    def test_edit(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).goToTeachPage().login(email, password)
        page = page.goToClassesPage().goToClassPage(class_name).goToClassSettingsPage()

        new_class_name = 'new ' + class_name
        assert not page.checkClassDetails({
            'name': new_class_name,
            'classmates_data_viewable': True,
        })

        page = page.changeClassDetails({
            'name': new_class_name,
            'classmates_data_viewable': True,
        })

        page = page.goToClassSettingsPage()
        new_class_name = 'new ' + class_name
        assert page.checkClassDetails({
            'name': new_class_name,
            'classmates_data_viewable': True,
        })

    def test_delete_empty(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).goToTeachPage().login(email, password)
        page = page.goToClassesPage().goToClassPage(class_name)
        assert not page.have_students()

        page = page.deleteClass()
        assert page.isDeleteConfirmShowing()
        page = page.cancelDelete()
        assert not page.isDeleteConfirmShowing()
        page = page.deleteClass()
        assert page.isDeleteConfirmShowing()
        page = page.confirmDelete()
        assert page.__class__.__name__ == 'TeachClassesPage'
        assert not page.have_classes()

    def test_delete_nonempty(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name = create_school_student_directly(access_code)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).goToTeachPage().login(email, password)
        page = page.goToClassesPage().goToClassPage(class_name)
        assert page.have_students()

        page = page.deleteClass()
        assert page.isDeleteConfirmShowing()
        page = page.cancelDelete()
        assert not page.isDeleteConfirmShowing()
        page = page.deleteClass()
        assert page.isDeleteConfirmShowing()
        page = page.confirmDelete()
        assert page.__class__.__name__ == 'TeachClassPage'
        assert is_class_nonempty_message_showing(self.browser)

    def test_transfer_cancel(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).goToTeachPage().login(email, password)
        page = page.goToClassesPage().goToClassPage(class_name).goToClassSettingsPage()

        page = page.transfer_class()
        assert page.get_tranfer_list_length() == 0
        page = page.cancel()
        assert page.__class__.__name__ == 'TeachClassPage'

    def test_transfer(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email_1)
        join_teacher_to_organisation(email_2, org_name, postcode)
        class_name, access_code = create_class_directly(email_1)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).goToTeachPage().login(email_1, password_1)
        page = page.goToClassesPage().goToClassPage(class_name).goToClassSettingsPage()

        page = transfer_class(page, 0)
        assert not page.have_classes()

        page = page.logout().goToTeachPage().login(email_2, password_2).goToClassesPage()
        assert page.have_classes()
        assert page.does_class_exist(class_name, access_code)
        page = page.goToClassPage(class_name)
        assert page.have_students()
        assert page.does_student_exist(student_name)
