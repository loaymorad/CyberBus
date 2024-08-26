import re

def is_strong(password):
    min_length = 8
    # if i want to change like if i want not uppercase just make it false
    uppercase = True
    lowercase = True
    digit = True
    sp_case = True
    
    if len(password) < min_length:
        return False
    
    # not any => checking is there an upper
    if uppercase and not any(char.isupper() for char in password):
        return False
    
    if lowercase and not any(char.islower()  for char in password):
        return False
    
    if digit and not any(char.isdigit()  for char in password):
        return False
    
    # re.search(what search for, search in)
    if sp_case and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
        
    return True
        