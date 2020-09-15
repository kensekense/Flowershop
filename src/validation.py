from scipy.spatial import distance
from src.db import get_db
from src.fingerprint import fp2text, text2fp

def validate (potential, poster, database):
    '''
    Takes a fingerprint which should be a numpy array
    and returns True or False given a certain established threshold gamma, adhering to the rules of NP/Bayes.
    '''

    #TODO: do proper adherence to rules of NP/Bayes to establish threshold for errors.

    #TODO: we can alter the code to do hamming sphere checks rather than brute force hamming distance checks.

    db_list = database.execute(
        'SELECT author_id, fingerprint, post_type'
        ' FROM post p'
    ).fetchall()

    for x in db_list:
        if (distance.hamming(potential, text2fp(x['fingerprint'])) == 0.0) and (x['post_type'] != "sponsor"):
            return (False, "Identical image detected.")

        #sponsor FLAG
        if (distance.hamming(potential, text2fp(x['fingerprint'])) == 0.0) and (x['post_type'] == "sponsor"):
            return ("sponsor", "Sponsored Post")

        #this is where we would need to alter to adhere to proper rules of NP/Bayes
        elif (distance.hamming(potential, text2fp(x['fingerprint'])) <= 0.2 and x['author_id'] != poster):
            return (False, "Repost detected. Please submit a claim.")

    return (True, "")
