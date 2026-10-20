"""Verify the worked example's model, numbers, and a seeded illustrative simulation."""
import json
import math
from pathlib import Path
import random

def collision(n,days=365):
    if n>days:return 1.0
    return 1-math.prod((days-i)/days for i in range(n))

def main():
    trials=20000;seed=20261020;rng=random.Random(seed)
    matches=sum(len(set(rng.randrange(365) for _ in range(23)))<23 for _ in range(trials))
    exact=collision(23);fixed=1-(364/365)**22
    assert collision(1)==0
    assert abs(collision(2)-1/365)<1e-12
    assert collision(366)==1
    assert collision(22)<.5<exact
    assert round(exact*100,1)==50.7
    assert 23*22//2==253
    assert round(fixed*100,1)==5.9
    result={'assumptions':['independent birthdays','uniform 365 days','no leap day'],
        'any_pair_22':collision(22),'any_pair_23':exact,
        'match_one_specified_person_among_22_others':fixed,'pairs_23':253,
        'warning':'Pair count explains intuition; 253/365 is not the collision probability. Pair events are not mutually exclusive.',
        'simulation':{'seed':seed,'trials':trials,'matches':matches,'estimate':matches/trials,
            'standard_error_under_model':math.sqrt(exact*(1-exact)/trials),
            'meaning':'Illustrative simulated classrooms, not observed human birthday data or proof of the exact formula.'}}
    path=Path(__file__).with_name('math-check.json')
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
