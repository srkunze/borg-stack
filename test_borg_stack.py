import os
import subprocess
from tempfile import mkdtemp
from unittest.case import TestCase


class BorgStackTestCase(TestCase):
    def setUp(self):
        tmpdir = mkdtemp(prefix='borg_stack_test_')
        self.path_to_repo = os.path.join(tmpdir, 'repo')
        subprocess.check_call(['borg', 'init', '--encryption', 'none', self.path_to_repo])
        self.source_dir = os.path.join(tmpdir, 'source_dir')
        os.mkdir(self.source_dir)
        self.test_file_path = os.path.join(self.source_dir, 'source_dir')
        with open(self.test_file_path, 'w') as file:
            file.write('borg-test-content')
    
    def test_create_and_list(self):
        output = subprocess.check_output(['borg-stack', 'list', self.path_to_repo + '::test_stack_*']).decode()
        self.assertNotIn('test_stack_1', output)
        self.assertNotIn('test_stack_2', output)
        self.assertNotIn('test_stack_3', output)

        subprocess.check_call(['borg-stack', 'create', self.path_to_repo + '::test_stack_1*', self.source_dir])
        output = subprocess.check_output(['borg-stack', 'list', self.path_to_repo + '::test_stack_*']).decode()
        self.assertIn('test_stack_1', output)
        self.assertNotIn('test_stack_2', output)
        self.assertNotIn('test_stack_3', output)

        subprocess.check_call(['borg-stack', 'create', self.path_to_repo + '::test_stack_2*', self.test_file_path])
        output = subprocess.check_output(['borg-stack', 'list', self.path_to_repo + '::test_stack_*']).decode()
        self.assertIn('test_stack_1', output)
        self.assertIn('test_stack_2', output)
        self.assertNotIn('test_stack_3', output)

        subprocess.check_call(['borg-stack', 'create', self.path_to_repo + '::test_stack_3*', self.source_dir])
        output = subprocess.check_output(['borg-stack', 'list', self.path_to_repo + '::test_stack_*']).decode()
        self.assertIn('test_stack_1', output)
        self.assertIn('test_stack_2', output)
        self.assertIn('test_stack_3', output)
