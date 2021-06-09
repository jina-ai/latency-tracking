import json

from prettytable import MARKDOWN, PrettyTable

with open('output/stats.json') as fp:
    d = json.load(fp)

x = PrettyTable()
x.field_names = ['Version', 'Index QPS', 'Query QPS']

index_qps = int(d[-1]['index_qps'])
query_qps = int(d[-1]['query_qps'])
x.add_row([f'current', index_qps, query_qps])

# temporally switch off the comparison
# We have no docker image tagged as `2.0.0rc3`
# We do not have convenient `from_ndarray` function in `2.0.0rc2`
# We shall switch on the avg computation and comparison with `2.0.0rc7`

# for dd in d[:-1][::-1]:
#     x.add_row([f'[`{dd["version"]}`](https://github.com/jina-ai/jina/tree/v{dd["version"]})', int(dd['index_qps']), int(dd['query_qps'])])

# avg_index_qps = sum(dd['index_qps'] for dd in d[:-1]) / len(d[:-1])
# avg_query_qps = sum(dd['query_qps'] for dd in d[:-1]) / len(d[:-1])

# delta_index = int((index_qps / avg_index_qps - 1) * 100)
# delta_query = int((query_qps / avg_query_qps - 1) * 100)

# if delta_index > 10:
#     emoji_index = '🐎🐎🐎🐎'
# elif delta_index > 5:
#     emoji_index = '🐎🐎'
# elif delta_index < -5:
#     emoji_index = '🐢🐢'
# elif delta_index < -10:
#     emoji_index = '🐢🐢🐢🐢'
# else:
#     emoji_index = '😶'

# if delta_query > 10:
#     emoji_query = '🐎🐎🐎🐎'
# elif delta_query > 5:
#     emoji_query = '🐎🐎'
# elif delta_query < -5:
#     emoji_query = '🐢🐢'
# elif delta_query < -10:
#     emoji_query = '🐢🐢🐢🐢'
# else:
#     emoji_query = '😶'

summary = f'## Latency summary\n ' \
          f'Current PR yields:\n' \
          f'  - **index QPS** at `{index_qps}`\n' \
          f'  - **query QPS** at `{query_qps}`\n\n' \
          f'## Breakdown'
        #   f'  - {emoji_index} **index QPS** at `{index_qps}`, delta to last 3 avg.: `{delta_index:+d}%`\n' \
        #   f'  - {emoji_query} **query QPS** at `{query_qps}`, delta to last 3 avg.: `{delta_query:+d}%`\n\n' \

print(summary)
x.set_style(MARKDOWN)
print(x)
print('\n\nBacked by [latency-tracking](https://github.com/jina-ai/latency-tracking).'
      ' Further commits will update this comment.')
