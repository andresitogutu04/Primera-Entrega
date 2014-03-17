from nose.tools import assert_raises, assert_true, assert_equal
from os import path as op
import os

from vispy.util import (config, sys_info, _TempDir, get_data_file,
                        set_data_dir, save_config)

temp_dir = _TempDir()


def test_sys_info():
    """Test printing of system information"""
    fname = op.join(temp_dir, 'info.txt')
    sys_info(fname)
    assert_raises(IOError, sys_info, fname)  # no overwrite
    with open(fname, 'r') as fid:
        out = ''.join(fid.readlines())
    keys = ['Python', 'Backend', 'Pyglet']  # 'GL version' only for non-GLUT
    for key in keys:
        assert_true(key in out)


def test_config():
    """Test vispy config methods and file downloading"""
    assert_raises(TypeError, config.update, data_path=dict())
    assert_raises(KeyError, config.update, foo='bar')  # bad key
    set_data_dir(temp_dir)
    assert_equal(config['data_path'], temp_dir)
    config['data_path'] = temp_dir
    print(config)  # __repr__
    get_data_file('CONTRIBUTING.txt')
    fid = open(op.join(temp_dir, 'test-faked.txt'), 'w')
    fid.close()
    get_data_file('test-faked.txt')  # this one shouldn't download
    assert_raises(RuntimeError, get_data_file, 'foo-nonexist.txt')
    orig_val = os.environ.get('_VISPY_CONFIG_TESTING', None)
    os.environ['_VISPY_CONFIG_TESTING'] = 'true'
    try:
        save_config()
    finally:
        if orig_val is not None:
            os.environ['_VISPY_CONFIG_TESTING'] = orig_val
        else:
            del os.environ['_VISPY_CONFIG_TESTING']
