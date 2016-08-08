from dateutil.parser import parse as parse_date


TAGS = [
    {'date': 'Sat Aug 06 12:00:23 2016 -0400', 'tag': '3.12.1', 'changeset': 'eec715eeb613'},
    {'date': 'Sat Aug 06 05:34:13 2016 -0400', 'tag': '3.11.0', 'changeset': '4d32d04f5b87'},
    {'date': 'Fri Aug 05 17:50:06 2016 -0400', 'tag': '3.11.0.rc.3', 'changeset': '54a53b87929a'},
    {'date': 'Thu Aug 04 16:41:54 2016 -0400', 'tag': '3.11.rc.3', 'changeset': '35b6df1b6288'},
    {'date': 'Tue Jul 26 15:32:10 2016 -0400', 'tag': '3.11.0.rc.1', 'changeset': '0e9a3c08074b'},
    {'date': 'Sun Jul 17 21:52:38 2016 -0400', 'tag': '3.10.1', 'changeset': '93f5435cb760'},
    {'date': 'Fri Jul 15 10:20:02 2016 -0400', 'tag': '3.10.0', 'changeset': 'b85349cda000'},
    {'date': 'Fri Jul 15 10:15:55 2016 -0400', 'tag': '3.9.3', 'changeset': '550c1bde37ba'},
    {'date': 'Thu May 26 12:12:41 2016 -0400', 'tag': '3.9.1', 'changeset': 'f33a2e80bb7d'},
    {'date': 'Sat Apr 23 11:57:52 2016 -0430', 'tag': '3.8.2', 'changeset': '7b65ff040d37'},
    {'date': 'Sat Apr 23 11:51:19 2016 -0430', 'tag': '3.8.2', 'changeset': 'dcf04d8bc8b8'},
    {'date': 'Fri Mar 18 13:42:17 2016 -0430', 'tag': '3.8.1', 'changeset': '24973b05e2b3'},
    {'date': 'Fri Mar 18 13:36:22 2016 -0430', 'tag': '3.8.1', 'changeset': '73ae26cd18a6'},
    {'date': 'Tue Mar 15 10:38:29 2016 -0430', 'tag': '3.8.0', 'changeset': '3d91da29c55b'},
    {'date': 'Sat Mar 05 23:11:38 2016 -0430', 'tag': '3.7.0', 'changeset': 'ed2efc22203b'},
    {'date': 'Wed Jan 27 13:33:09 2016 -0430', 'tag': '3.6.7', 'changeset': '2c1a83f0c41d'},
    {'date': 'Wed Dec 02 11:09:22 2015 -0430', 'tag': '3.6.6', 'changeset': '8b2cf44a7081'},
    {'date': 'Sun Sep 13 15:53:01 2015 -0430', 'tag': '3.6.5', 'changeset': '133b7df6c7ab'},
    {'date': 'Sat Sep 12 10:17:18 2015 -0430', 'tag': '3.6.4', 'changeset': '0e26738d1828'},
    {'date': 'Tue Aug 25 14:35:55 2015 -0430', 'tag': '3.6.3', 'changeset': 'aaa7d106bc87'},
    {'date': 'Sun Jun 07 03:45:55 2015 -0430', 'tag': '3.6.1', 'changeset': '23f412394324'},
    {'date': 'Tue May 12 17:28:46 2015 -0430', 'tag': '3.6.0', 'changeset': '11292cf2ccb7'},
    {'date': 'Thu Mar 12 14:13:21 2015 -0430', 'tag': '3.5.1', 'changeset': '8a49b22121bb'},
    {'date': 'Thu Nov 27 08:43:06 2014 -0430', 'tag': '3.4.3', 'changeset': '7f65185dbc0a'},
    {'date': 'Mon Nov 10 12:48:19 2014 -0430', 'tag': '3.4.2', 'changeset': '185bb6c3ce36'},
    {'date': 'Thu Sep 25 16:37:05 2014 -0430', 'tag': '3.4.2-rc.2', 'changeset': '1b2fa81e49d9'},
    {'date': 'Wed Aug 13 21:58:38 2014 -0430', 'tag': '3.4.1', 'changeset': '6e15bd4fb34f'},
    {'date': 'Tue Aug 12 04:32:36 2014 -0430', 'tag': '3.4.0', 'changeset': 'ab617d16de4b'},
    {'date': 'Tue Jul 22 17:43:23 2014 -0430', 'tag': '3.3.0', 'changeset': '4a5d984172ef'},
    {'date': 'Tue Jul 22 15:15:23 2014 -0430', 'tag': '3.2.2-rc.3', 'changeset': 'abb7f2552fdc'},
    {'date': 'Tue Jul 22 15:11:52 2014 -0430', 'tag': '3.2.2-rc.3', 'changeset': 'e048d2c26f61'},
    {'date': 'Tue Jul 22 15:06:51 2014 -0430', 'tag': '3.2.2-rc.2', 'changeset': '956dda7bb4af'},
    {'date': 'Tue Jul 22 14:06:59 2014 -0430', 'tag': '3.2.2-rc.1', 'changeset': '11621b7253e4'},
    {'date': 'Mon Jul 21 00:06:42 2014 -0430', 'tag': '3.2.1', 'changeset': '9c5fa7203027'},
    {'date': 'Sat Jul 19 19:19:33 2014 -0430', 'tag': '3.2.1-rc.1', 'changeset': '297baf0d0258'},
    {'date': 'Sat Jul 19 19:04:33 2014 -0430', 'tag': '3.2.1-rc.1', 'changeset': 'fa21428f146b'},
    {'date': 'Thu Jul 17 15:24:25 2014 -0430', 'tag': '3.2.0', 'changeset': '357ffa03213b'},
    {'date': 'Thu Jul 17 14:27:23 2014 -0430', 'tag': '3.2.0', 'changeset': '7156166abb2a'},
    {'date': 'Wed Jul 16 03:08:41 2014 -0430', 'tag': '3.1.3-rc.1', 'changeset': '154960af7104'},
    {'date': 'Wed Jul 16 03:02:34 2014 -0430', 'tag': '3.1.3-rc.1', 'changeset': 'ba00cfb8550f'},
    {'date': 'Wed Jul 16 03:01:34 2014 -0430', 'tag': '3.1.3-rc.1', 'changeset': '2d2be224b949'},
    {'date': 'Mon Jul 14 10:29:04 2014 -0430', 'tag': '3.1.2', 'changeset': '91d5e12d3bd2'},
    {'date': 'Mon Jul 14 00:05:08 2014 -0430', 'tag': '3.1.2', 'changeset': '575bb74270a9'},
    {'date': 'Sun Jul 13 23:56:18 2014 -0430', 'tag': '3.1.2', 'changeset': '78bd3ee2823c'},
    {'date': 'Sun Jul 13 23:53:17 2014 -0430', 'tag': '3.1.2', 'changeset': 'cee0c8028ddb'},
    {'date': 'Sun Jul 13 16:36:21 2014 -0430', 'tag': '3.1.1', 'changeset': '4a6a49386391'},
    {'date': 'Mon Jul 07 22:31:43 2014 -0430', 'tag': '3.0.5-rc.1', 'changeset': '6bbe58d6cd26'},
    {'date': 'Sat Jul 05 09:57:22 2014 -0430', 'tag': '3.1.0', 'changeset': '8fbcb7779341'},
    {'date': 'Fri Jul 04 13:28:48 2014 -0430', 'tag': 'pre_left_recursion', 'changeset': '2f66cd275c23'},
    {'date': 'Thu Jul 03 10:34:20 2014 -0430', 'tag': '3.0.5-rc.1', 'changeset': '6bbe58d6cd26'},
    {'date': 'Tue Jul 01 08:29:06 2014 -0430', 'tag': '3.0.4', 'changeset': '3640d0d70ff5'},
    {'date': 'Fri Jun 27 14:45:17 2014 -0430', 'tag': '3.0.3', 'changeset': 'b62fa26d79c1'},
    {'date': 'Fri Jun 27 12:50:43 2014 -0430', 'tag': '3.0.2', 'changeset': '3dd7afb8965b'},
    {'date': 'Sun Jun 22 08:46:08 2014 -0430', 'tag': '3.0.0', 'changeset': '3f16b76862e6'},
    {'date': 'Sun Jun 22 08:44:43 2014 -0430', 'tag': '3.0.1', 'changeset': 'c83e7f0f84f1'},
    {'date': 'Thu Jun 12 15:05:21 2014 -0430', 'tag': '3.0.0-rc.8', 'changeset': '3f16b76862e6'},
    {'date': 'Thu Jun 12 15:00:45 2014 -0430', 'tag': '3.0.0-rc.7', 'changeset': '6a3f1d9f7d9e'},
    {'date': 'Thu Jun 12 14:31:21 2014 -0430', 'tag': '3.0.0-rc.7', 'changeset': '1ac00ac4a7cc'},
    {'date': 'Wed Jun 11 15:13:51 2014 -0430', 'tag': '3.0.0-rc.6', 'changeset': '8a1b61ed5018'},
    {'date': 'Sun Jun 08 14:17:54 2014 -0430', 'tag': '3.0.0-rc.5', 'changeset': 'b3fb82448241'},
    {'date': 'Sun Jun 08 10:54:25 2014 -0430', 'tag': '2.4.3', 'changeset': '5d46d2c966a5'},
    {'date': 'Sat Jun 07 15:15:47 2014 -0430', 'tag': '3.0.0-rc.4', 'changeset': 'e755ed737a9a'},
    {'date': 'Wed Jun 04 03:02:36 2014 -0430', 'tag': '3.0.0-rc.3', 'changeset': '5b6384b687e4'},
    {'date': 'Tue Jun 03 15:43:15 2014 -0430', 'tag': '3.0.0-rc.2', 'changeset': '80d9efb56cc8'},
    {'date': 'Tue Jun 03 15:39:48 2014 -0430', 'tag': '3.0.0-rc.2', 'changeset': '90bce1c4370c'},
    {'date': 'Tue Jun 03 15:39:18 2014 -0430', 'tag': '3.0.0-rc.2', 'changeset': 'fd6b7c66dd86'},
    {'date': 'Tue Jun 03 15:31:32 2014 -0430', 'tag': '3.0.0-rc.2', 'changeset': '59cbfc94ff7e'},
    {'date': 'Tue Jun 03 14:05:39 2014 -0430', 'tag': '3.0.0-rc.2', 'changeset': 'e96eda1c74e3'},
    {'date': 'Mon Jun 02 16:28:45 2014 -0430', 'tag': '3.0.0-rc.0', 'changeset': '19ce52f12e6b'},
    {'date': 'Tue May 27 09:17:35 2014 -0430', 'tag': '2.5.0-rc.1', 'changeset': 'c2fff743e6e2'},
    {'date': 'Mon May 26 11:31:39 2014 -0430', 'tag': '2.4.2', 'changeset': 'bfbb1521bc58'},
    {'date': 'Mon May 26 11:01:09 2014 -0430', 'tag': '2.4.2', 'changeset': '59e35b38322a'},
    {'date': 'Wed Apr 30 15:46:04 2014 -0430', 'tag': 'pre-r_speer', 'changeset': '0125a52e2c5c'},
    {'date': 'Tue Apr 22 10:28:20 2014 -0430', 'tag': '2.4.1', 'changeset': '76d49635116b'},
    {'date': 'Sat Apr 19 11:20:14 2014 -0430', 'tag': '2.4.1', 'changeset': 'c90988c88fec'},
    {'date': 'Fri Apr 04 13:14:46 2014 -0430', 'tag': '2.5.0-rc.0', 'changeset': '9311692444b1'},
    {'date': 'Sat Mar 08 15:54:46 2014 -0430', 'tag': '2.4.0', 'changeset': '78fbe9b3e17b'},
    {'date': 'Fri Mar 07 14:36:23 2014 -0430', 'tag': 'pre_automodel', 'changeset': 'fd6b7c66dd86'},
    {'date': 'Wed Nov 27 14:50:20 2013 -0430', 'tag': '2.3.0', 'changeset': '32dd301ec69f'},
    {'date': 'Wed Nov 06 08:29:21 2013 -0430', 'tag': '2.2.1', 'changeset': '0cfd93dbb444'},
    {'date': 'Wed Nov 06 08:28:02 2013 -0430', 'tag': '2.2.2', 'changeset': 'ab9df6423399'},
    {'date': 'Tue Oct 08 16:37:23 2013 -0430', 'tag': '2.2.0', 'changeset': 'c4f24315d78a'},
    {'date': 'Tue Oct 08 16:34:45 2013 -0430', 'tag': '2.2.0', 'changeset': '083ff8917064'},
    {'date': 'Fri Sep 06 22:59:15 2013 -0430', 'tag': '2.1.0', 'changeset': 'c0b844886904'},
    {'date': 'Fri Sep 06 17:08:16 2013 -0430', 'tag': '2.1.0', 'changeset': '5a5f8f43b13e'},
    {'date': 'Fri Sep 06 16:59:06 2013 -0430', 'tag': '2.1.0', 'changeset': 'ae05c0d1f64d'},
    {'date': 'Fri Sep 06 16:57:58 2013 -0430', 'tag': '2.1.0', 'changeset': 'bd601db9da8a'},
    {'date': 'Thu Aug 15 07:37:26 2013 -0430', 'tag': '2.0.4', 'changeset': '9a0239847bfe'},
    {'date': 'Thu Jul 04 23:32:16 2013 -0430', 'tag': '2.0.3', 'changeset': '08d89d8ea755'},
    {'date': 'Wed Jun 26 05:58:41 2013 -0450', 'tag': '2.0.2', 'changeset': '22bbd52f7c80'},
    {'date': 'Wed Jun 26 06:18:41 2013 -0430', 'tag': '2.0.2', 'changeset': '22bbd52f7c80'},
    {'date': 'Wed Jun 26 06:17:13 2013 -0430', 'tag': '2.0.2', 'changeset': '7d1486e084c5'},
    {'date': 'Sat May 25 16:02:24 2013 -0430', 'tag': '2.0.1', 'changeset': 'e9bfb9381537'},
    {'date': 'Wed May 22 21:04:36 2013 -0430', 'tag': '2.0.0', 'changeset': '1bc2fe7ea393'},
    {'date': 'Sun May 19 21:38:25 2013 -0430', 'tag': '2.0.0', 'changeset': '14b5dfd9e31e'},
    {'date': 'Sun May 19 21:37:17 2013 -0430', 'tag': '2.0.0', 'changeset': '09fd79fb6855'},
    {'date': 'Sun May 19 20:28:27 2013 -0430', 'tag': '2.0.0', 'changeset': '7a499b29b719'},
    {'date': 'Sun May 19 19:10:59 2013 -0430', 'tag': '2.0.0-rc.2', 'changeset': '566f55fb73cc'},
    {'date': 'Sun May 19 18:56:46 2013 -0430', 'tag': '2.0.0-rc.2', 'changeset': 'c66578fc0d8f'},
    {'date': 'Sun May 12 02:02:20 2013 -0430', 'tag': '2.0.0-rc.1', 'changeset': '1010ba5953f0'},
    {'date': 'Thu May 02 17:51:45 2013 -0430', 'tag': '1.4.0', 'changeset': '171fb2c4c203'},
    {'date': 'Tue Apr 30 21:37:02 2013 -0430', 'tag': '1.4.0-rc.1', 'changeset': '0ba0add86926'},
    {'date': 'Thu Apr 11 18:17:55 2013 -0430', 'tag': '1.3.0', 'changeset': 'ea4804849767'},
    {'date': 'Sun Apr 07 11:44:54 2013 -0430', 'tag': '1.3.0-rc.2', 'changeset': '34d98084347c'},
    {'date': 'Sat Mar 30 11:50:32 2013 -0430', 'tag': '1.3.0-rc.1', 'changeset': '3b3ed4bb3556'},
    {'date': 'Sat Mar 30 11:05:37 2013 -0430', 'tag': '1.3.0-rc.1', 'changeset': '8a57ebaaf154'},
    {'date': 'Tue Mar 19 14:32:28 2013 -0430', 'tag': '1.2.1', 'changeset': 'cc7c11238eca'},
    {'date': 'Sat Mar 16 22:51:26 2013 -0430', 'tag': '1.2.0', 'changeset': '94d60d1acef7'},
    {'date': 'Sat Mar 16 22:48:26 2013 -0430', 'tag': '1.2.0', 'changeset': '4aaa67c8f768'},
    {'date': 'Fri Feb 22 08:30:03 2013 -0430', 'tag': '1.1.0', 'changeset': '9142272d295a'},
    {'date': 'Thu Feb 21 11:24:50 2013 -0430', 'tag': '1.1.0', 'changeset': '61cefd20fca0'},
    {'date': 'Sat Feb 09 11:05:15 2013 -0430', 'tag': '1.0.0', 'changeset': '7e61371f5395'},
    {'date': 'Tue Feb 05 22:19:56 2013 -0430', 'tag': '1.0rc4', 'changeset': 'b4c9cd09891d'},
    {'date': 'Mon Feb 04 11:39:17 2013 -0430', 'tag': '1.0rc3', 'changeset': 'aa6b6428e3ad'},
    {'date': 'Sat Feb 02 20:24:50 2013 -0430', 'tag': '1.0rc2', 'changeset': '6eec9c1caabc'},
    {'date': 'Thu Jan 31 07:37:21 2013 -0430', 'tag': '1.0rc1', 'changeset': 'b78e397ed284'},
    {'date': 'Wed Jan 30 08:08:17 2013 -0430', 'tag': '1.0rc1', 'changeset': 'e84354fbff94'},
    {'date': 'Sun Jan 13 18:07:34 2013 -0430', 'tag': '0.1', 'changeset': '64bab5d7fe96'},
]


def main():
    for tag in TAGS:
        parsed = parse_date(tag['date'])
        if parsed is None:
            print('NONE', tag['date'])
            continue
        tag['date'] = parsed

    tags_by_date = list(tag['tag'] for tag in reversed(sorted(TAGS, key=lambda t: t['date'])))
    # remove rc tags
    tags_by_date = [tag for tag in tags_by_date if tag.replace('.', '').isdigit() and len(tag) > 3]

    prev = tags_by_date[0]
    for tag in tags_by_date[1:]:
        if tag.split('.')[:2] != prev.split('.')[:2]:
            print('[{prev}]: https://bitbucket.org/apalala/grako/branches/compare/{prev}%0D{tag}'.format(tag=tag, prev=prev))
            prev = tag

    print()
    for tag in TAGS:
        if tag['tag'] in tags_by_date:
            print('### [{tag}] {date}'.format(tag=tag['tag'], date=tag['date'].strftime('%Y-%m-%d')))


if __name__ == '__main__':
    main()
