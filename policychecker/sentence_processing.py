from sentence_class import sent
from completness_analysis import analyzer
import re
from scipy import spatial
import json
import pickle

templates_rep = ''
sbert = ''
nlp = ''
checker = ''

def bigram_matching(input1, templates):
    find_match = False
    for ngram in templates:
        words = ngram.rsplit()
        pattern = re.compile(r'%s' % "\s+".join(words),
            re.IGNORECASE)
        if len(pattern.findall(input1)) > 0:
            find_match = True
    return find_match

def semantic_similarity(input1, template):
    find_match = False
    threshold = 0.7

    r1 = sbert.encode(input1)
    score =  1 - spatial.distance.cosine(r1, template)
    if score > threshold:
        find_match = True
    return find_match

def content_identification(content, template_name):
    
    f = open('meta_data/template_plaintext.pickle', 'rb')
    temp = pickle.load(f)
    find_match = False
    find_match = bigram_matching(content, temp[template_name])
        
    if not find_match:
        for template in templates_rep[template_name]:
            find_match = semantic_similarity(content, template)

    return find_match

def token_lemma(word):
    return " ".join([token.lemma_ for token in nlp(word)])

def purpose_analysis(arguments):
    for argument in arguments:
        if (argument.find('for') == 0 or argument.find('to') == 0 or argument.find('in order to') == 0 or argument.find('so as to') == 0 or argument.find('so that') 
        or argument.find('so')== 0 or argument.find('in response')== 0):
            checker.set_S('Data processing purpose') 
        if content_identification(argument, 'legal_obligation_template'):
            checker.set_S('legal basis') 
            checker.set_S_legal('legal obligation')
        elif content_identification(argument, 'performance_contract_template'):
            checker.set_S('legal basis')
            checker.set_S_legal('performance contract')
        elif content_identification(argument, 'legitmate_interest_template'):
            checker.set_S('legal basis')
            checker.set_S_legal('legitmate interest')
        elif content_identification(argument, 'legitmate_interest_details_template'):
            checker.set_S('legal basis')
            checker.set_S('Interest pursued')
            checker.set_S_interest(argument)
        elif content_identification(argument, 'public_interest_template'):
            checker.set_S_legal('public interest')
            checker.set_S('legal basis')
        elif content_identification(argument, 'vital_interest_template'):
            checker.set_S_legal('vital interest')
            checker.set_S('legal basis')

def retention(roles_argument, NER_labels, sentence_obj):
    has_keeper = False
    has_data = False
    has_retention_time = False
    has_retention_description = False
    for_purpose = []
    has_consent = []
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip() 
        if role == 'V':
            if argument in sentence_obj.get_passive_verb_list():
                has_keeper = True
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'CONTROLLER':
                    has_keeper = True
        elif role == 'ARG1':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'DATA':
                    has_data = True
        elif role == 'ARGM-TMP':

            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'TIME':
                    has_retention_time = True 
            if not has_retention_time:
                if content_identification(argument, 'retention_criteria'):
                    has_retention_description = True

            if content_identification(argument, 'consent_template'):
                has_consent.append(argument)
        elif role == 'ARGM-PRP' or role == 'ARGM-PNC':
            for_purpose.append(argument)
        elif role == 'ARGM-MNR' or role == 'ARGM-ADV' or role == 'ARG2':
            if content_identification(argument, 'consent_template'):
                has_consent.append(argument)
        elif role == 'ARGM-NEG':
            return -1

    if has_keeper and has_data:
        if len(for_purpose) > 0:
            purpose_analysis(for_purpose)
        if len(has_consent) > 0:
            checker.set_S('legal basis')
            checker.set_S_legal('user consent')

    if has_keeper and has_data and has_retention_time:
        checker.set_S('Data retention time limit')


    if has_keeper and has_data and has_retention_description:
        checker.set_S('Data retention criteria')


def collection(roles_argument, NER_labels, sentence_obj):

    has_controller_entity = False
    has_data_entity = False
    has_data_entity_specfic = False
    has_sender_general_description = False
    has_sender_third_party = False
    has_sender_third_party_category = False
    has_sender_user = False
    for_purpose = []
    has_consent = []
    negated = False

    for srl_structure in roles_argument:
        # print(NER_labels)
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'CONTROLLER':
                    has_controller_entity = True

        elif role == 'ARG1':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'DATA':
                    has_data_entity = True
                    if not content_identification(argument, 'data_general_description'):
                        has_data_entity_specfic = True
                if ent in argument and NER_label == 'USER':
                    has_sender_user = True
        elif role == 'ARG2':
            if content_identification(argument, 'third_party_general_description'):
                has_sender_general_description = True
            else:
                for ent, NER_label in NER_labels.items():
                    if ent in argument and (NER_label == 'ORG' or NER_label == 'COM'):
                        has_sender_third_party = True
                    elif ent in argument and NER_label == 'USER' :
                        has_sender_user = True
            if content_identification(argument, 'third_party_specfic_description'):
                has_sender_third_party_category = True
        elif role == 'ARGM-PRP' or role == 'ARGM-PNC':
            for_purpose.append(argument)
    
        elif role == 'ARGM-MNR' or role == 'ARGM-ADV' or role == 'ARGM-TMP':
            if content_identification(argument, 'consent_template'):
                has_consent.append(argument)
            if role == 'ARGM-ADV' or role == 'ARGM-TMP':
                for ent, NER_label in NER_labels.items():
                    if ent in argument and NER_label == 'USER' :
                        has_sender_user = True
            if content_identification(argument, 'user_consequence_template'):
                checker.set_S('User obligation and consequences')
        elif role == 'ARGM-NEG':
            negated = True

    if not negated:
        if has_controller_entity and has_data_entity:
            if len(for_purpose) > 0:
                purpose_analysis(for_purpose)

            if len(has_consent) > 0:
                checker.set_S_legal('user consent')
                checker.set_S('legal basis')
                
        if has_controller_entity and has_data_entity and has_sender_user:
            checker.set_13(True)

        if has_controller_entity and has_data_entity and (has_sender_third_party or has_sender_general_description):
            checker.set_14(True)
            if has_sender_third_party or has_sender_third_party_category:
                checker.set_S('Source of the personal data')
            if has_data_entity_specfic:
                checker.set_S('Categories of the personal data')


def sharing(roles_argument, NER_labels, sentence_obj):

    has_sender_controller = False
    has_sender_user = False
    has_sender_third_party = False

    has_data = False
    has_reciever_com = False
    has_reciever_controller = False
    has_reciever_user = False 

    has_unknown_sender = False
    
    for_purpose = []
    has_consent = []

    negated = False
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'V':
            if argument in sentence_obj.get_passive_verb_list():
                has_unknown_sender = True
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'CONTROLLER':
                    has_sender_controller = True
                if ent in argument and NER_label == 'USER':
                    has_sender_user = True
                if ent in argument and (NER_label == 'ORG' or NER_label == 'COM'):
                    has_sender_third_party = True 
            if content_identification(argument, 'third_party_general_description') or content_identification(argument, 'third_party_specfic_description'):
                has_sender_third_party = True 
        elif role == 'ARG1':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'DATA':
                    has_data = True
        elif role == 'ARG2':
            for ent, NER_label in NER_labels.items():
                if ent in argument and (NER_label == 'ORG' or NER_label == 'COM'):
                    has_reciever_com = True
                elif ent in argument and NER_label == 'CONTROLLER' :
                    has_reciever_controller = True
                elif ent in argument and NER_label == 'USER' :
                    has_reciever_user = True
        elif role == 'ARGM-PRP' or role == 'ARGM-PNC':
            for_purpose.append(argument)

        elif role == 'ARGM-MNR'or role == 'ARGM-ADV' or role == 'ARGM-TMP':
            if content_identification(argument, 'consent_template'):
                has_consent.append(argument)
            if content_identification(argument, 'user_consequence_template'):
                checker.set_S('User obligation and consequences')
        elif role == 'ARGM-NEG':
            negated = True

    if not negated:
        if has_sender_user and has_data:
            checker.set_13(True)
            checker.set_P('data collection')

            if len(for_purpose) > 0:
                purpose_analysis(for_purpose)
            if len(has_consent) > 0:
                checker.set_S_legal('user consent')
                checker.set_S('legal basis')


        if has_sender_controller and has_data and has_reciever_com:
            checker.set_S('Recipients of the personal data')
            if len(for_purpose) > 0:
                purpose_analysis(for_purpose)
            if len(has_consent) > 0:
                checker.set_S_legal('user consent') 
                checker.set_S('legal basis')

        if has_sender_third_party and has_data and has_reciever_controller:
            checker.set_S('Categories of personal data')
            if len(for_purpose) > 0:
                purpose_analysis(for_purpose)
            if len(has_consent) > 0:
                checker.set_S_legal('user consent')
                checker.set_S('legal basis')

        if has_sender_controller and has_data and not has_reciever_user:
            checker.set_P('data sharing')
            if len(for_purpose) > 0:
                purpose_analysis(for_purpose)
            if len(has_consent) > 0:
                checker.set_S_legal('user consent')
                checker.set_S('legal basis')




def use(roles_argument, NER_labels, sentence_obj):
    has_user = False
    has_data = False
    has_decision_system = False
    for_purpose = []
    has_consent = []
    has_controller_id = False
    negated = False
    has_unknown_user = False
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'V':
            if argument in sentence_obj.get_passive_verb_list():
                has_unknown_user = True
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'CONTROLLER':
                    has_user = True
                elif ent in argument and (NER_label == 'COM' or NER_label == 'ORG'):
                    has_controller_id = True
        elif role == 'ARG1':
            for ent, NER_label in NER_labels.items():
                if (ent in argument and NER_label == 'DATA'):
                    has_data = True
            if not has_data and content_identification(argument, 'decision_system_template'):
                has_decision_system = True
        elif role == 'ARGM-PRP' or role == 'ARGM-PNC' or role == 'ARG2':
            for_purpose.append(argument)

        elif role == 'ARGM-MNR'or role == 'ARGM-ADV' or role == 'ARGM-TMP':
            if content_identification(argument, 'consent_template'):
                has_consent.append(argument)
            if content_identification(argument, 'user_consequence_template'):
                checker.set_S('User obligation and consequences')
        elif role == 'ARGM-NEG':
            negated = True
            
    if not negated:
        if (has_data or has_decision_system) and (has_user or has_controller_id or has_unknown_user):
            checker.set_13(True)
            if len(for_purpose) > 0:
                purpose_analysis(for_purpose)

            if len(has_consent) > 0:
                checker.set_S_legal('user consent')
                checker.set_S('legal basis')

        if has_user and has_data:
            checker.set_13(True)

        if has_user and has_decision_system:
            checker.set_S('Automatic decision system in use')


def transfer(roles_argument, NER_labels, sentence_obj):
    has_transferor = False
    has_data = False
    has_dest = False
    for_purpose = []
    has_consent = []

    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip() 
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'CONTROLLER':
                    has_transferor = True
        elif role == 'ARG1':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'DATA':
                    has_data = True
        elif role == 'ARGM-LOC':
            has_dest = True
        elif role == 'ARGM-PRP' or role == 'ARGM-PNC':
            for_purpose.append(argument)
        elif role == 'ARGM-MNR' or role == 'ARGM-ADV' or role == 'ARGM-TMP':
            if content_identification(argument, 'consent_template'):
                has_consent.append(argument)
                checker.set_S_legal('user consent')
                checker.set_S('legal basis')
        elif role == 'ARGM-NEG':
            return -1
    
    if has_transferor and has_data:
        checker.set_S('International data transfer behavior')
        if len(for_purpose) > 0:
            purpose_analysis(for_purpose)

        if len(has_consent) > 0:
            checker.set_S_legal('user consent')
            checker.set_S('legal basis')

def consent_giving(roles_argument, NER_labels, sentence_obj):
    has_giver = False
    has_consent = []
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'USER':
                    has_giver = True
        elif role == 'V' and argument in ['grant', 'consent', 'agree']:
            has_consent.append(argument)

        elif role == 'ARG1' and content_identification(argument, 'consent_template'):
            has_consent.append(argument)

    if has_giver and len(has_consent) > 0:
        checker.set_S_legal('user consent')
        checker.set_S('legal basis')


def consent_soliciting(roles_argument, NER_labels, sentence_obj):
    has_solicitor = False
    has_consent = []

    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'CONTROLLER':
                    has_solicitor = True
        elif role == 'ARG1' and content_identification(argument, 'consent_template'):
                has_consent.append(argument)
    if has_solicitor and len(has_consent) > 0:
        checker.set_S_legal('user consent')
        checker.set_S('legal basis')


def transfer_safeguarding(roles_argument, NER_labels, sentence_obj):
    has_relier = False
    has_relied_object_adequacy_decision = False
    has_relied_object_safeguard = False

    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'CONTROLLER':
                    has_relier = True
        elif role == 'ARG1':
            if content_identification(argument, 'adequacy_decision_template'):
                has_relied_object_adequacy_decision = True
            elif content_identification(argument, 'transfer_safeguard_template'):
                has_relied_object_safeguard = True
        elif role == 'ARGM-PRP' or role == 'ARGM-PNC':
            purpose_analysis(argument)
        elif role == 'ARGM-MNR' or role == 'ARGM-ADV' or role == 'ARGM-TMP':
            if content_identification(argument, 'consent_template'):
                checker.set_S_legal('user consent')
                checker.set_S('legal basis')

    if has_relier and has_relied_object_adequacy_decision:
        checker.set_S('Adequacy decision')

    if has_relier and has_relied_object_safeguard:
        checker.set_S('Transfer safeguards')


def rights_entitle_request(roles_argument, NER_labels, sentence_obj):
    has_requester = False
    passive_verb = False
    rights_argument = ''
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'V' and argument in sentence_obj.get_passive_verb_list():
            passive_verb = True

    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if not passive_verb:
            if role == 'ARG0':
                for ent, NER_label in NER_labels.items():
                    if ent in argument and NER_label == 'USER':
                        has_requester = True
            elif role == 'ARG1':
                rights_argument = argument
        else:
            if role == 'ARG2':
                for ent, NER_label in NER_labels.items():
                    if ent in argument and NER_label == 'USER':
                        has_requester = True
            elif role == 'ARG1':
                rights_argument = argument

    if has_requester and rights_argument:
        if content_identification(rights_argument, 'data_access_template'):
            checker.set_S('Right to data access')
        if content_identification(rights_argument, 'data_erasure_template'):
            checker.set_S('Right to data erasure')
        if content_identification(rights_argument, 'data_rectification_template'):
            checker.set_S('Right to data rectification')
        if content_identification(rights_argument, 'data_export_template'):
            checker.set_S('Right to data portability')
        if content_identification(rights_argument, 'processing_restriction_template'):
            checker.set_S('Right to restrict processing')
        if content_identification(rights_argument, 'processing_objection_template'):
            checker.set_S('Right to object processing')
        if content_identification(rights_argument, 'consent_withdraw_template'):
            checker.set_S('Right to withdraw consent')
        if content_identification(rights_argument, 'logde_complaints_template'):
            checker.set_S('Right to lodge complaints')
        

def rights_AREE(roles_argument, NER_labels, sentence_obj, topic):

    has_user = False
    has_data = False 
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'USER':
                    has_user = True
        elif role == 'ARG1':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'DATA':
                    has_data = True 

    if has_user and has_data:
        checker.set_S(topic)

def rights_restrict_object(roles_argument, NER_labels, sentence_obj, topic):
    has_user = False
    has_processing = False 
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'USER':
                    has_user = True
        elif role == 'ARG1':
            if content_identification(argument, 'data_processing_template'):
                has_processing = True

    if has_processing and has_user and topic == 'right_processing_restriction':
        checker.set_S('Right to restrict processing')

    elif has_processing and has_user and topic == 'right_processing_objection':
        checker.set_S('Right to object processing')


def consent_withdraw(roles_argument, NER_labels, sentence_obj):
    has_user = False
    has_consent = False 
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'USER':
                    has_user = True
        elif role == 'ARG1':
            if content_identification(argument, 'consent_template'):
                has_consent = True

    if has_user and has_consent:
        checker.set_S('Right to withdraw consent')

def logde_complaints(roles_argument, NER_labels, sentence_obj):
    has_user = False
    has_compliant = False 
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'USER':
                    has_user = True
        elif role == 'ARG1':
            if content_identification(argument, 'logde_complaints_template'):
                has_compliant = True

    if has_user and has_compliant:
        checker.set_S('Right to lodge complaints')


def obligation_fulfillment(roles_argument, NER_labels, sentence_obj):
    has_controller = False
    legal_obligation = False 
    contract = False
    legitmate_interest = False
    legitmate_interest_detail = False
    public_interest = False
    vital_interest = False
    legal_object = []
    for srl_structure in roles_argument:
        role = srl_structure[0]
        argument = srl_structure[1].strip()
        if role == 'ARG0':
            for ent, NER_label in NER_labels.items():
                if ent in argument and NER_label == 'CONTROLLER':
                    has_controller = True
        elif role == 'ARG1' or role == 'ARGM-PRP' or role == 'ARGM-PNC':
            if content_identification(argument, 'legal_obligation_template'):
                legal_obligation = True
            elif content_identification(argument, 'performance_contract_template'):
                contract = True
            elif content_identification(argument, 'legitmate_interest_template'):
                legitmate_interest = True
            elif content_identification(argument, 'legitmate_interest_details_template'):
                legitmate_interest_detail = True
                legal_object.append(argument)
            elif content_identification(argument, 'public_interest_template'):
                public_interest = True
            elif content_identification(argument, 'vital_interest_template'):
                vital_interest = True

    if has_controller:
        if legal_obligation:
            checker.set_S('legal basis') 
            checker.set_S_legal('legal obligation')
        if contract:
            checker.set_S('legal basis')
            checker.set_S_legal('performance contract')
        if legitmate_interest:
            checker.set_S('legal basis')
            checker.set_S_legal('legitmate interest')
        if legitmate_interest_detail:
            checker.set_S('legal basis')
            checker.set_S('Interest pursued')
            for object in legal_object:
                checker.set_S_interest(object)
        if public_interest:
            checker.set_S_legal('public interest')
            checker.set_S('legal basis')
        if vital_interest:
            checker.set_S_legal('vital interest')
            checker.set_S('legal basis')
  
def contact_details(text, sentence_obj):
    email = re.findall('\S+@\S+', text)

    phone_number_clean = re.findall('^\\+?[1-9][0-9]{7,14}$', text)
    phone_number_complex = re.findall('^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$', text)

    if email or phone_number_clean or phone_number_complex:
        checker.set_S('Contact Information')
    else:
        if text.split(' '):
            for text in text.split(' '):
                text.rstrip()
                email = re.findall('\S+@\S+', text)
                phone_number_clean = re.findall('^\\+?[1-9][0-9]{7,14}$', text)
                phone_number_complex = re.findall('^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$', text)
                if email or phone_number_clean or phone_number_complex:
                    checker.set_S('Contact Information')

def controller_identity(text, sentence_obj, controller_id):
    if controller_id != '' and controller_id in text:
        checker.set_S('Controller identity')

def dispacher(action_roles_arguments, NER_labels, sentence_obj):
    for action_roles_argument in action_roles_arguments:
        action = action_roles_argument[0]    
        if action == 'data_collection_practice':
            collection(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'data_sharing_practice':
            sharing(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'data_using_practice':
            use(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'data_retention_practice':
            retention(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'data_transfer_practice':
            transfer(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'consent_giving_practice':
            consent_giving(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'consent_soliciting_practice':
            consent_soliciting(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'transfer_safeguarding_practice':
            transfer_safeguarding(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'consent_withdraw_practice':
            consent_withdraw(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'data_access_practice':
            rights_AREE(action_roles_argument[1], NER_labels, sentence_obj, 'Right to data access')
        elif action == 'data_rectification_practice':
            rights_AREE(action_roles_argument[1], NER_labels, sentence_obj, 'Right to data rectification')
        elif action == 'data_erasure_practice':
           rights_AREE(action_roles_argument[1], NER_labels, sentence_obj, 'Right to data erasure')
        elif action == 'data_export_practice':
            rights_AREE(action_roles_argument[1], NER_labels, sentence_obj, 'Right to data portability')
        elif action == 'processing_restriction_practice':
            rights_restrict_object(action_roles_argument[1], NER_labels, sentence_obj, 'right_processing_restriction')
        elif action == 'processing_objection_practice':
            rights_restrict_object(action_roles_argument[1], NER_labels, sentence_obj, 'right_processing_objection')
        elif action == 'rights_entitle_practice' or action == 'rights_request_practice':
            rights_entitle_request(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'obligation_fulfill_practice':
            obligation_fulfillment(action_roles_argument[1], NER_labels, sentence_obj)
        elif action == 'logde_complaints_practice':
            logde_complaints(action_roles_argument[1], NER_labels, sentence_obj)


def sentence_reciever(filename, sentences, controller_id, app_title, template_representations, output_folder, sbert_model,nlp_model, SRL_predictor_model, evaluation):
    global templates_rep
    global sbert 
    global checker
    global nlp

    checker = analyzer(output_folder)
    nlp = nlp_model
    sbert = sbert_model

    templates_rep = template_representations
    sentence_objs = []
    single_mode = True
    SRL_list = []

    for index, sentence in enumerate(sentences):
        if len(sentence) >= 700 or len(sentence.split(' ')) > 500:
            sentence = 'too long'
        if not single_mode:
            sentence_obj = sent(sentence, controller_id, app_title, SRL_list[index])
        else:
            sentence_obj = sent(sentence, controller_id, app_title, None)
            sentence_obj.set_srl(SRL_predictor_model)

        sentence_obj.set_ner(nlp)
        sentence_obj.predicate_extraction()
        if sentence_obj.no_verb:
            controller_identity(sentence, sentence_obj, controller_id)
            contact_details(sentence, sentence_obj)
            sentence_objs.append(sentence_obj)
            continue
        action_roles_arguments =  sentence_obj.get_semantic_roles_and_arguments()
        NER_labels = sentence_obj.named_entity()
        dispacher(action_roles_arguments, NER_labels, sentence_obj)
        controller_identity(sentence, sentence_obj, controller_id)
        contact_details(sentence, sentence_obj)

        sentence_objs.append(sentence_obj)

    checker.run(filename)


