import requests
import json
import numpy as np
from collections import OrderedDict

def array_to_hash(x):
    x_tupled = None
    if type(x) == list:
        x_tupled = tuple(x)
    elif type(x) == np.ndarray:
        x_tupled = tuple(list(x.flatten()))
    elif type(x) == tuple:
        x_tupled = x
    else:
        raise RuntimeError('unexpected type of input: {}'.format(type(x)))
    return hash(tuple(map(float, x_tupled)))

def almostEqual(x, y):
    return abs(x - y) < 1e-3


class Grader(object):
    def __init__(self):
        self.submission_page = 'https://www.coursera.org/api/onDemandProgrammingScriptSubmissions.v1'
        self.assignment_key = '2ksCns1AEeiQGAocUzg3rg'
        self.parts = OrderedDict([
                    ('6IBOp', 'negative_samples'),
                    ('KFgw6', 'positive_samples'),
                    ('AdVS6', 'resource_unique_values'),
                    ('Qmiy0', 'logloss_mean'),
                    ('5UJeq', 'logloss_std'),
                    ('3JTkU', 'accuracy_6'),
                    ('N0VEy', 'best_model_name'),
                    ('xmS1J', 'num_trees'),
                    ('ztywb', 'mean_logloss_cv'),
                    ('FaDLS', 'logloss_std_1'),
                    ('jFOSe', 'iterations_overfitting'),
                    ('inxm1', 'auc_550'),
                    ('QRox8', 'feature_importance_top3'),
                    ('4t0CV', 'most_important'),
                    ('C8JOy', 'shap_influence'),
                    ('R50wr', 'speedup'),
                    ('eA8X5', 'final_auc')])
        self.answers = {key: None for key in self.parts}

    @staticmethod
    def ravel_output(output):
        '''
           If student accedentally submitted np.array with one
           element instead of number, this function will submit
           this number instead
        '''
        if isinstance(output, np.ndarray) and output.size == 1:
            output = output.item(0)
        return output

    def submit(self, email, token):
        submission = {
                    "assignmentKey": self.assignment_key, 
                    "submitterEmail": email, 
                    "secret": token, 
                    "parts": {}
                  }
        for part, output in self.answers.items():
            if output is not None:
                submission["parts"][part] = {"output": output}
            else:
                submission["parts"][part] = dict()
        request = requests.post(self.submission_page, data=json.dumps(submission))
        response = request.json()
        if request.status_code == 201:
            print('Submitted to Coursera platform. See results on assignment page!')
        elif u'details' in response and u'learnerMessage' in response[u'details']:
            print(response[u'details'][u'learnerMessage'])
        else:
            print("Unknown response from Coursera: {}".format(request.status_code))
            print(response)

    def status(self):
        print("You want to submit these numbers:")
        for part_id, part_name in self.parts.items():
            answer = self.answers[part_id]
            if answer is None:
                answer = '-'*10
            print("Task {}: {}".format(part_name, answer))
               
    def submit_part(self, part, output):
        self.answers[part] = output
        print("Current answer for task {} is: {}".format(self.parts[part], output))

    def submit_tag(self, tag, output):
        part_id = [k for k, v in self.parts.items() if v == tag]
        if len(part_id)!=1:
            raise RuntimeError('cannot match tag with part_id: found {} matches'.format(len(part_id)))
        part_id = part_id[0]
        self.submit_part(part_id, str(self.ravel_output(output)))
