
# 标准库
import pickle





# ------------------------------------------------
# result 

def save_var(path, data):
    """
        保存变量数据
        path 变量存储路径
        data 数据
    """
    with open(path, 'wb') as f:
        pickle.dump(data, f)
    return None


def read_var(path):
    """
        读取变量存储数据
        path 目标数据路径
    """

    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data


# func_prefix = lambda p_str, str1: p_str+'_'+str1
func_prefix = lambda p_str, str1: p_str+'_'+str1

def parse_result_data(params, value_params, list_params, prefix_str=None):
    
    if not isinstance(params, dict):
        return None
    
    for key in params:
        d1 = params[key]
        
        if isinstance(key, float) or isinstance(key, int): key = str(key)
        
        if prefix_str != None:
            new_key = func_prefix(prefix_str, key)
        else:
            new_key = key
        
        if isinstance(d1, dict):
            parse_result_data(d1, value_params, list_params, new_key)
            continue
        
        if isinstance(d1, float) or isinstance(d1, str) or isinstance(key, int):
            value_params[new_key] = d1
            continue
        
        if isinstance(d1, list):
            list_params[new_key] = d1
            continue
        
    return value_params, list_params


# ------------------------------------------
# 测试
def test_var_read_and_save():
    test = {'a':[1,2,3],'b':'asdf'}
    save_var('temp.var', test)
    print(read_var('temp.var'))

