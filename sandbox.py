from screeninfo import get_monitors

m = get_monitors()
print(m)

print(m[0].width)
print(m[0].height)
    