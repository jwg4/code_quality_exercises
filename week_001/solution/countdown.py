def evaluate(method, running_sum):
    """
        Check if an expression matches the target.
        If it does, print it and return True
    """
    if eval(method) == target:
        # The string expression evaluates to the target
        if method not in list_methods:
            list_methods.append(method)
            print(f'Eval: {method}')
        return True
    if running_sum == target:
        # The value of the expression matches the target.
        # 
        # TODO: Shouldn't this only happen when the first if is True?
        if method not in list_methods:
            list_methods.append(method)
            print(f'Running sum: {method}')
        return True
    return False


def new_total(total, item, operation):
    """
        Combine total and item using an arithmetic operation.
    """
    if operation == "+":
        return total + item
    if operation == "-":
        return total - item
    if operation == "*":
        return total * item
    if operation == "/" and item != 0:
        return total / item
    return ""


def solve(array, total=0, method="", list_method=[]):
    """
        Use the numbers in array to make the value in target

        array: the numbers which can be used
        total: a running total to which we can add
        method: the string which contains an expression which evaluates to total
            method should be "" iff total is 0
        list_method: unused
    """
    if len(array) == 0:
        return

    for (index, item) in enumerate(array):
        add_method, sub_method, mul_method, div_method = "", "",  "", ""
        add_total, sub_total, mul_total, div_total = 0, 0, 0, 0

        methods = [add_method, sub_method, mul_method, div_method]
        totals = [add_total, sub_total, mul_total, div_total]
        str_func = ["+", "-", "*", "/"]

        remaining = array[:index] + array[index+1:]

        for index_1 in range(len(methods)):
            if method != "":
                # We already have a partial expression.
                # Combine the new number with it.
                methods[index_1] = (
                    method
                    + str_func[index_1]
                    + str(array[index])
                )
                totals[index_1] = new_total(total, item, str_func[index_1])
            else:
                # We don't yet have a partial expression
                # Make one, using a number from array on its own.
                # total will be 0
                # TODO: No point using '*' or '/' here.
                # TODO: Is it legit to use '-' here?
                methods[index_1] = str(array[index])
                totals[index_1] = new_total(total, item, str_func[index_1])

        for index_2 in range(len(methods)):
            # Check if either one of the totals or one of the operations
            # has given the target. If so, return now. If not carry on.
            try:
                if evaluate(methods[index_2], totals[index_2]):
                    methods[index_2] = ""
                    totals[index_2] = 0
                    return
            except Exception:
                pass

        for index_3 in range(len(methods)):
            try:
                # We recurse on each of the values, combined to the total
                # by each of the possible operations, and pass through the
                # partial expression which shows how we got there.
                solve(
                    remaining,
                    total=totals[index_3],
                    method=methods[index_3]
                )
            except Exception:
                # Eg. if we divide by zero we just ignore and carry on.
                pass


# Six integers as the numbers to use.
# One target three-digit integer
array = [100, 75, 50, 25, 6, 3]
target = 952

# Todo: We should return list_methods from solve()
list_methods = []
solve(array)
if list_methods == []:
    # Didn't find a solution
    print("None")
