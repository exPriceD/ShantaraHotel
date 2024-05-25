def isValid(s: str) -> bool:
    if len(s) % 2 != 0:
        return False

    close = (")", "]", "}")
    open = ("(", "[", "{")

    a = list(s)
    stack = [a[0]]
    for i in range(1, len(a)):
        stack.append(a[i])
        if len(stack) < 2:
            continue
        if stack[-1] in close and stack[-2] in open:
            if stack[-1] == ")" and stack[-2] == "(":
                stack.pop()
                stack.pop()
            elif stack[-1] == "]" and stack[-2] == "[":
                stack.pop()
                stack.pop()
            elif stack[-1] == "}" and stack[-2] == "{":
                stack.pop()
                stack.pop()
    if stack:
        return False
    return True

print(isValid("()"))
