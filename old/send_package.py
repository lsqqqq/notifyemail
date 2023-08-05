from __future__ import print_function, division

import argparse
import time


def main(args):
    import notifyemail as notify

    notify.Reboost(mail_host='smtp.163.com', mail_user='xxxxx', mail_pass='xxxxx',
                   default_reciving_list=['xxxx'],
                   log_root_path='log', max_log_cnt=5)

    time.sleep(2)

    if args.target_path is None:
        target_path = input('input a target_path to grab the package:')
    else:
        target_path = args.target_path

    if args.receive_user is None:
        receive_user = input('input a receive_user to deliver the package:')
    else:
        receive_user = args.receive_user
        notify.add_text('Send components by email with NotifyEmail \n')
        notify.add_text('target_path：' + target_path + '\n')

    print('target_path:', target_path)
    print('receive_user', receive_user)

    notify.add_file(target_path)
    notify.send_log(receive_user)


def get_args_parser():
    parser = argparse.ArgumentParser(description='Send components by email with NotifyEmail')

    parser.add_argument('--receive_user', default=None, type=str, help='which user will receive the email letter')

    # Enviroment parameters
    parser.add_argument('--target_path', default=None, type=str, help='what will be sent in the email letter')

    return parser


if __name__ == '__main__':
    parser = get_args_parser()
    args = parser.parse_args()
    main(args)
