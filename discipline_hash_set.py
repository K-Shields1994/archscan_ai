#Hash set for all disciplines in large format documents

#Create hash set
discipline_hash_set = set()

#Add elements to hash set
discipline_hash_set.add('architectural')
discipline_hash_set.add('civil')
discipline_hash_set.add('site')
discipline_hash_set.add('demolition')
discipline_hash_set.add('electrical')
discipline_hash_set.add('equipment layout')
discipline_hash_set.add('fire protection')
discipline_hash_set.add('food service')
discipline_hash_set.add('general')
discipline_hash_set.add('interiors')
discipline_hash_set.add('landscape')
discipline_hash_set.add('life safety')
discipline_hash_set.add('mechanical')
discipline_hash_set.add('hvac')
discipline_hash_set.add('mech piping')
discipline_hash_set.add('plumbing')
discipline_hash_set.add('security')
discipline_hash_set.add('shop')
discipline_hash_set.add('contractor drawing')
discipline_hash_set.add('structural')
discipline_hash_set.add('telecommunications')
discipline_hash_set.add('audio visual')

def check_set(s):
    if s in discipline_hash_set:
        return s
    else:
        print(f"{s} is not in discipline hash set")

#Testing
str = 'security'
print(check_set(str))
