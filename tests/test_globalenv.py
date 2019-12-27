import pytest
from sym_lis import GlobalEnv, Env

env = GlobalEnv()

def test_env_runs():
    assert env.eval_str('(+ 1 4)') == 5

def test_env_wrong_init():
    with pytest.raises(TypeError):
        env2 = GlobalEnv(env=55)

def test_env_special_init():
    env_empty = GlobalEnv(Env())
    # test public keys
    assert len([k for k in env_empty.keys() if k and k[0] != '_']) == 0

