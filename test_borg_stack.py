import os
import subprocess
from tempfile import mkdtemp
from unittest.case import TestCase


class BorgStackTestCase(TestCase):
    def test_borg_stack_create(self):
        tmpdir = mkdtemp(prefix='borg_stack_test_')
        borg_repository_path = os.path.join(tmpdir, 'repo')
        subprocess.check_call(['borg', 'init', '--encryption', 'none', borg_repository_path])

        source_dir = os.path.join(tmpdir, 'source_dir')
        os.mkdir(source_dir)
        test_file = os.path.join(source_dir, 'source_dir')
        with open(test_file, 'w') as file:
            file.write('borg-test-content')
        subprocess.check_call(['borg-stack', 'create', borg_repository_path + '::test_stack_1*', source_dir])
        subprocess.check_call(['borg-stack', 'create', borg_repository_path + '::test_stack_2*', test_file])
        subprocess.check_call(['borg-stack', 'create', borg_repository_path + '::test_stack_3*', source_dir])

        output = subprocess.check_output(['borg-stack', 'list', borg_repository_path + '::test_stack_*']).decode()
        self.assertIn('test_stack_1', output)
        self.assertIn('test_stack_2', output)
        self.assertIn('test_stack_3', output)
