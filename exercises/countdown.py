def evaluate (method,running_sum):
    if eval(method) == target:
        if method not in list_methods:
            list_methods.append(method)
            print (f'Eval: {method}')
        return True 
    if running_sum == target:
        if method not in list_methods:
            list_methods.append(method)
            print (f'Running sum: {method}')
        return True 
    return False

def new_total (total,item,operation):
    if operation == "+": return total + item
    if operation == "-": return total - item
    if operation == "*": return total * item
    if operation == "/" and item != 0: return total / item 
    return ""

def solve (array,total=0,method="",list_method=[]):
    if len(array) == 0:
        return 

    for (index,item) in enumerate(array):
        add_method, sub_method, mul_method, div_method = "", "", "", ""
        add_total, sub_total, mul_total, div_total = 0, 0, 0,0

        methods = [add_method, sub_method, mul_method, div_method]
        totals = [add_total, sub_total, mul_total, div_total]
        str_func = ["+", "-", "*", "/"]

        remaining = array[:index] + array[index+1:]

        for index_1 in range (len(methods)):
            if method != "":
                methods[index_1] = method + str_func[index_1] + str(array[index])
                totals[index_1] = new_total(total,item,str_func[index_1])
            else:
                methods[index_1] = str(array[index])
                totals[index_1] = new_total(total,item,str_func[index_1])

        for index_2 in range (len(methods)):
            try: 
                if evaluate(methods[index_2], totals[index_2]):
                    methods[index_2]=""
                    totals[index_2]=0
                    return 
            except Exception:
                pass 

        for index_3 in range (len(methods)):
            try:
                solve(remaining, total= totals[index_3],method= methods[index_3])
            except Exception:
                pass 


array = [100,75,50,25,6,3]
target = 952
list_methods = []
solve(array)
if list_methods == []: print ("None")
