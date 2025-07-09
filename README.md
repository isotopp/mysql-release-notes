# MySQL Release Notes

This is a Python project (done with uv) that downloads all MySQL release notes,
puts them into a `release_notes` folder,
and then parses all the release notes, pushing them into a database.

It uses click (but we currently actually have no options), SQL Alchemy and mysqlclient to connect to a database.

It generates a schema (not preserving any data),
and then fills the schema with all the release notes that we have.

![](mysql_releases.png)

The schema is a simple encoded star schema: For each release, we have many issues,
and for each issue we have a number of properties.
Properties are not stored as text, but are encoded, and we store only the property id.

Properties are:
- command (issue relates to a command such as `mysqldump`)
- bug (issue bug number)
- option (issue releates to a command line option such as `--alldatabases`)
- page (issue links to a documentation page)
- statvar (issue mentions a status variable)
- sysvar (issue mentions a system variable)
- tag (issue is filed under a headline, or issue text starts with a keyword)
- issue thanks (a contributor is named in a very specific way)
- workload (issue mentions a worklog number)

We can now check how many bugs have been addressed per release,
who contributed the most,
if the number of changes to a subsystem such as Replication changes over time,
or other data.

We can also show what bugs or worklog items an upgrade between any two versions would address,
and which subsystems are touched.

# Issues

The data is extracted from HTML, 
which means the data quality has issues,
and we need a system of fixer callbacks on import.

Specifically:
- The tag extraction needs work.
- sysvar needs to clean up leading double dashes and `-` to `_`, 
  so that `--admin-tls-version` -> `admin_tls_version`.
- command needs cleanup: there are commands with spaces and line breaks, and other random elements.
- `option` is a wild mix of MySQL Options and compiler options.

and of course

- This is a hackish single evening project and the code is ugly.

If you have contributions, please send a MR.

# Example usage

```mysql
select t.contributor, 
       min(r.release_date), min(r.version), 
       max(r.release_date), max(r.version), 
       count(i.text) as cnt 
  from `release` r 
  join issue i on r.id = i.release_id 
  join issue_thanks it on i.id = it.issue_id
  join thanks t on it.thanks_id = t.id 
group by t.contributor 
order by cnt desc;
+--------------------------------------+---------------------+----------------+---------------------+----------------+-----+
| contributor                          | min(r.release_date) | min(r.version) | max(r.release_date) | max(r.version) | cnt |
+--------------------------------------+---------------------+----------------+---------------------+----------------+-----+
| Meta                                 | 2023-07-18          | 8.0.34         | 2023-10-25          | 8.2.0          |  14 |
| Facebook                             | 2020-07-13          | 8.0.21         | 2023-10-25          | 8.2.0          |   7 |
| Shaohua Wang and the team at Alibaba | 2024-10-15          | 8.0.40         | 2025-01-21          | 9.2.0          |   6 |
| Jonathan Albrecht                    | 2024-01-16          | 8.0.37         | 2024-04-30          | 8.4.0          |   6 |
| Daniël van Eeden                     | 2023-07-18          | 8.1.0          | 2025-04-15          | 9.3.0          |   6 |
| Shaohua Wang                         | 2023-10-25          | 5.7.44         | 2024-04-30          | 8.4.0          |   5 |
| Kaiwang Chen                         | 2021-04-20          | 8.0.24         | 2025-01-21          | 9.2.0          |   5 |
| Sho Nakazono                         | 2024-07-01          | 8.0.38         | 2024-10-15          | 9.1.0          |   4 |
| Tencent                              | 2023-07-18          | 8.0.34         | 2023-10-25          | 8.2.0          |   4 |
| Dmitry Lenev                         | 2023-04-18          | 8.0.33         | 2024-10-15          | 9.1.0          |   4 |
| Hao Lu                               | 2023-10-25          | 8.0.35         | 2024-04-30          | 8.4.0          |   4 |
| Daniel Nichter                       | 2024-10-15          | 8.0.40         | 2024-10-15          | 9.1.0          |   3 |
| Rahul Malik                          | 2025-01-21          | 8.0.41         | 2025-01-21          | 9.2.0          |   3 |
| Mengchu Shi and the team at Alibaba  | 2025-04-15          | 8.0.42         | 2025-04-15          | 9.3.0          |   3 |
| Martin Alderete                      | 2024-04-30          | 8.0.37         | 2024-07-01          | 9.0.0          |   3 |
| Marcelo Altmann                      | 2023-01-17          | 5.7.41         | 2025-04-15          | 9.3.0          |   3 |
| Ke Yu                                | 2024-07-01          | 8.0.38         | 2024-07-01          | 9.0.0          |   3 |
| Baolin Huang and the team at Alibaba | 2025-04-15          | 8.0.42         | 2025-04-15          | 9.3.0          |   3 |
| Huaxiong Song                        | 2024-07-01          | 8.0.38         | 2024-07-01          | 9.0.0          |   3 |
| Hope Lee                             | 2021-01-18          | 8.0.23         | 2022-01-18          | 8.0.28         |   3 |
| Gordon Wang                          | 2024-10-15          | 8.0.40         | 2024-10-15          | 9.1.0          |   3 |
| Casa Zhang and the Tencent team      | 2022-01-18          | 8.0.28         | 2022-01-18          | 8.0.28         |   3 |
| Yin Peng and the Tencent team        | 2024-04-30          | 8.0.37         | 2025-01-21          | 9.2.0          |   3 |
| George Ma and the Alibaba team       | 2025-01-21          | 8.0.41         | 2025-01-21          | 9.2.0          |   3 |
| Henning Pöttker                      | 2024-10-15          | 8.0.40         | 2024-10-15          | 9.1.0          |   3 |
| Yewei Xu and the Tencent team        | 2023-04-18          | 5.7.42         | 2023-04-18          | 8.0.33         |   2 |
| Øystein Grøvlen                      | 2021-10-19          | 8.0.27         | 2022-01-18          | 8.0.28         |   2 |
| Namrata Bhave                        | 2022-07-26          | 8.0.30         | 2022-07-26          | 8.0.30         |   2 |
| Minha Jeong                          | 2024-07-01          | 8.4.1          | 2024-07-01          | 9.0.0          |   2 |
| Richard Dang                         | 2023-10-25          | 8.0.37         | 2024-04-30          | 8.2.0          |   2 |
| Daniyaal Khan                        | 2025-04-15          | 9.3.0          | 2025-04-15          | 9.3.0          |   2 |
| Sam James                            | 2024-01-16          | 8.0.36         | 2024-04-30          | 8.4.0          |   2 |
| Dirkjan Bussink                      | 2019-04-25          | 5.7.26         | 2024-07-01          | 9.0.0          |   2 |
| Yuxiang Jiang and the Tencent team   | 2022-07-26          | 5.7.39         | 2022-07-26          | 8.0.30         |   2 |
| Kento Takeuchi                       | 2023-07-18          | 8.0.34         | 2023-07-18          | 8.1.0          |   2 |
| Yura Sorokin                         | 2023-07-18          | 8.0.34         | 2023-07-18          | 8.1.0          |   2 |
| karry zhang                          | 2024-01-16          | 8.0.36         | 2024-01-16          | 8.3.0          |   2 |
| xiaoyang chen                        | 2024-04-30          | 8.0.37         | 2024-04-30          | 8.4.0          |   2 |
| Jeremy Cole                          | 2020-07-13          | 5.7.33         | 2021-01-18          | 8.0.21         |   2 |
| Zongzhi Chen                         | 2024-07-01          | 9.0.0          | 2024-07-01          | 9.0.0          |   1 |
| Adam Cable                           | 2021-07-20          | 8.0.26         | 2021-07-20          | 8.0.26         |   1 |
| Yubao Liu                            | 2021-10-19          | 8.0.27         | 2021-10-19          | 8.0.27         |   1 |
| Simon Mudd                           | 2024-10-15          | 9.1.0          | 2024-10-15          | 9.1.0          |   1 |
| Sinisa Milivojevic                   | 2023-04-18          | 8.0.33         | 2023-04-18          | 8.0.33         |   1 |
| Song Zhibai                          | 2022-01-18          | 8.0.28         | 2022-01-18          | 8.0.28         |   1 |
| Zetang Zeng                          | 2023-07-18          | 5.7.43         | 2023-07-18          | 5.7.43         |   1 |
| Xingyu Yang and the Tencent team     | 2024-10-15          | 9.1.0          | 2024-10-15          | 9.1.0          |   1 |
| Tianfeng Li                          | 2024-01-16          | 8.3.0          | 2024-01-16          | 8.3.0          |   1 |
| Wen He and the Tencent team          | 2023-10-25          | 8.2.0          | 2023-10-25          | 8.2.0          |   1 |
| Kanno Satoshi                        | 2025-04-15          | 9.3.0          | 2025-04-15          | 9.3.0          |   1 |
| Alex Xing                            | 2024-07-01          | 9.0.0          | 2024-07-01          | 9.0.0          |   1 |
| Alexi Xing                           | 2024-01-16          | 8.3.0          | 2024-01-16          | 8.3.0          |   1 |
| Bin Wang                             | 2024-01-16          | 8.3.0          | 2024-01-16          | 8.3.0          |   1 |
| Brian Yue                            | 2022-04-26          | 8.0.29         | 2022-04-26          | 8.0.29         |   1 |
| Dan McCombs                          | 2023-04-18          | 8.0.33         | 2023-04-18          | 8.0.33         |   1 |
| dc huang                             | 2023-04-18          | 8.0.33         | 2023-04-18          | 8.0.33         |   1 |
| Dimitry Kudryavtsev                  | 2022-10-11          | 8.0.31         | 2022-10-11          | 8.0.31         |   1 |
| J D                                  | 2022-07-26          | 8.0.30         | 2022-07-26          | 8.0.30         |   1 |
| Samuel Chiang                        | 2024-01-16          | 8.3.0          | 2024-01-16          | 8.3.0          |   1 |
| Konno Satoshi                        | 2025-01-21          | 9.2.0          | 2025-01-21          | 9.2.0          |   1 |
| Laurynas Biveinis                    | 2023-01-17          | 8.0.32         | 2023-01-17          | 8.0.32         |   1 |
| Lee Adria                            | 2024-04-30          | 8.4.0          | 2024-04-30          | 8.4.0          |   1 |
| Mike Wang                            | 2025-04-15          | 9.3.0          | 2025-04-15          | 9.3.0          |   1 |
| Niklas Keller                        | 2023-04-18          | 8.0.33         | 2023-04-18          | 8.0.33         |   1 |
| Pieter Oliver                        | 2025-04-15          | 9.3.0          | 2025-04-15          | 9.3.0          |   1 |
| Pika Mander                          | 2025-04-15          | 9.3.0          | 2025-04-15          | 9.3.0          |   1 |
+--------------------------------------+---------------------+----------------+---------------------+----------------+-----+
66 rows in set (0.00 sec)
```
