import argparse
import os
import re
import sys
from glob import glob
from pathlib import Path

user_ands = []
user_ors = []
no_run_list = []


def process_tags_expression(user_tag_expression):
    global user_ands
    global user_ors
    global no_run_list

    user_ands = []
    user_ors = []

    cleanup_pattern = r'[\[\]{})]'
    copyUserArgs = re.sub(cleanup_pattern, '', user_tag_expression)
    copyUserArgs = re.sub(r'\s+', ' ', copyUserArgs)

    # Extract tags containing '~@' or 'and ~@' or '~@norun'
    no_run_list = re.findall(r'(?:and )?~@(?:[-_\w]*|norun)', copyUserArgs)

    # Remove extracted tags from the expression
    for tag in no_run_list:
        copyUserArgs = copyUserArgs.replace(tag, '')

    copyUserArgs = ' '.join(copyUserArgs.split())
    # remove the unwanted and in the no_run_list
    no_run_list = [item.lstrip('and ~') for item in no_run_list]

    # Process user expression
    if 'and (' in copyUserArgs:
        andBracket = copyUserArgs.split('and (')
        andAry = andBracket[0].split('and')
        andAry = [strItm.strip() for strItm in andAry if strItm.strip().startswith('@')]
        user_ands.extend(andAry)

        orAry = andBracket[1].split(' or ')
        orAry = [strItm.strip() for strItm in orAry if strItm.strip().startswith('@')]
        user_ors.extend(orAry)

    elif 'or' in copyUserArgs:
        orAry = copyUserArgs.split('or ')
        orAry = [strItm.strip() for strItm in orAry if strItm.strip().startswith('@')]
        user_ors.extend(orAry)

    else:
        if copyUserArgs.strip() != '':
            andAry = copyUserArgs.split('and ')
            andAry = [strItm.strip() for strItm in andAry if strItm.strip().startswith('@')]
            user_ands.extend(andAry)


def filter_feature_and_scenarios(features_dir, result_dir, tags):
    Path(result_dir).mkdir(parents=True, exist_ok=True)
    for f in os.listdir(result_dir):
        os.remove(os.path.join(result_dir, f))

    process_tags_expression(tags)

    total_features = 0
    total_scenarios = 0

    if features_dir.endswith('.feature'):
        feature_files = [os.path.normpath(feature_path) for feature_path in glob(features_dir)]
    else:
        feature_files = [os.path.normpath(feature_path) for feature_path in glob(features_dir + '/*.feature')]

    for feature_file in feature_files:
        with open(feature_file, 'r') as f:
            feature_content = f.read().strip()

        # Replace multiple blank lines with a single blank line
        feature_content = re.sub(r'\n\s*\n', '\n\n', feature_content)
        # Remove lines starting with #
        feature_content = re.sub(r'^#.*\n', '', feature_content, flags=re.MULTILINE)
        feature_content = re.sub(r'\n\s*\n', '\n\n', feature_content)

        filename_head = f'{result_dir}/par_{os.path.splitext(os.path.basename(feature_file))[0]}'
        feature_blocks = feature_content.split('\n\n')

        if 'Background: ' in feature_blocks[1]:
            feature_header = feature_blocks[0] + '\n\n' + feature_blocks[1] + '\n\n\n'
            feature_blocks.pop(1)
        else:
            feature_header = feature_blocks[0] + '\n\n\n'

        feature_tags = feature_header.split('\n')[0].split()
        if no_run_list and set(no_run_list).issubset(set(feature_tags)):
            continue
        feature_cases = [case for case in feature_blocks[1:]]

        # re-initialize the feature file buffer
        sequence_cases = []

        sequence_cases.append(feature_header)
        found_cases = 0
        for case in feature_cases:
            case_as_list = case.split('\n')
            case_tags = case_as_list[0].split()

            buffer_tags = case_as_list[0].strip() if case.strip().startswith('@') else ''
            buffer_case = '\n'.join(case_as_list[1:]) if case.strip().startswith('@') else case

            all_tags = case_tags + feature_tags

            if no_run_list and set(no_run_list).issubset(set(all_tags)):
                continue
            if user_ands and not set(user_ands).issubset(set(all_tags)):
                continue
            if user_ors and not set(all_tags).intersection(set(user_ors)):
                continue

            sequence_cases.append(' ' + buffer_tags + ' @final\n')
            sequence_cases.append(buffer_case + ' \n\n')
            found_cases += 1

        # Only when at least 1 Scenario has been identified, flush the buffer into new file
        if found_cases > 0:
            total_features += 1
            total_scenarios += found_cases
            with open(f'{filename_head}.feature', 'w', encoding='utf-8') as result:
                result.writelines(sequence_cases)

    print(f'{total_scenarios} Scenarios found in {total_features} Features files')

    return total_scenarios


def main():
    args = None
    test_expressions = ['{@web}', '  {  @web    and @regression    and ~@norun}', '{~@norun and @web and (@test1 or @test2)}',
                        '{~@norun and (@test1 or @test2)}', '{@web and ~@browser and @sanity and ~@norun}', '{~@norun}', '{@sanity or @regression}',
                        '{@web and @browser and ~@norun and (@regression or @Sanity)}', '{@web and ~@norun and (@regression or @Sanity)}',
                        '{  ~@web   and   @browser   and   @checkout   and    ~@norun and (  @regression   or   @Sanity    )}',
                        '{  ~@web   and   @browser   and   @checkout   and    @norun and (  @test1   or   @test2    )}',
                        '{  @web   and   @regression   and    @norun and (  @test1   or   @test2    )}', '{@web and (@regression or @Sanity)}',
                        '{  @web   and   ~@browser   and   ~@checkout   and    @norun and (  @regression   or   @Sanity    )}',
                        '{@web and ~@norun and (@p1)}', '@web', '', '{~@test-2}', '{~@norun and @web}',
                        '{@web and @browser and ~@norun and (@regression or @Sanity or @titan-ic-ship)}',
                        '{@web-browser and @browser-desktop and ~@no-run and (@regression or @Sanity or @titan-ic-ship)}']

    try:
        parser = argparse.ArgumentParser(description='Allows the user to run either (1)Veriy-Tags or (2)Verify-Tags-Extract-Files')
        parser.add_argument('argopt', type=int, help='Specify which option you want to run')
        parser.add_argument("argparam", type=str, nargs="?", default=None, help="Tag Expression")

        args = parser.parse_args()
    except SystemExit:
        print('To test only Tag Expression Processor, please choose: ')
        print('\t $ python bdd_tags_expression_processor.py 1')
        print('\t $ python bdd_tags_expression_processor.py 1 "{@web}"')
        print('To test filtering Feature files based on Tag Expression, please choose: ')
        print('\t $ python bdd_tags_expression_processor.py 2')
        print('\t $ python bdd_tags_expression_processor.py 2 "{@web}"')
        sys.exit(1)

    argopt = args.argopt
    argparam = args.argparam

    def verify_sample_tag_expressions(one_sample_tag=None):
        if one_sample_tag is None:
            print('Considering all the expression from the sample test_expressions provided in the code')
            for expression in test_expressions:
                process_tags_expression(expression)
                print(f'\nGiven expression: {expression}\n\t Result: --> NORUNs: {no_run_list},  ANDs: {user_ands}, ORs: {user_ors}')
        else:
            print('Considering the given expression as everything available')
            process_tags_expression(one_sample_tag)
            print(f'Given expression: {one_sample_tag}\n\t Result: --> NORUNs: {no_run_list},  ANDs: {user_ands}, ORs: {user_ors}')

    def verify_extracted_files(input_path: str, output_path: str, one_sample_tag=None):
        if one_sample_tag is None:
            for expression in test_expressions:
                filter_feature_and_scenarios(input_path, output_path, expression)
                print(f'{expression} ... completed.. please check files\n')
        else:
            filter_feature_and_scenarios(input_path, output_path, one_sample_tag)
            print(f' {one_sample_tag} ... completed.. please check files')

    if argopt == 1:
        if argparam:
            verify_sample_tag_expressions(argparam)
        else:
            verify_sample_tag_expressions(test_expressions)
    elif argopt == 2:
        print("Ensure that you have input_path='features/web', output_path='features/final'. Default assumption is not created")
        input("Do you want to continue? (yes/no): ").strip().lower()
        if argparam:
            verify_extracted_files(input_path='features/web', output_path='features/final', one_sample_tag=argparam)
        else:
            verify_extracted_files(input_path='features/web', output_path='features/final')
    else:
        print('Choose only from 1 or 2 as choices in the argument')


if __name__ == '__main__':
    main()
