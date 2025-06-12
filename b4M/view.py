
import sys
import os
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt

if __package__ is None or __package__ == '':
    # current directory visibility
    import utils as ut
    import settings as st
else:
    # current package visibility
    from . import utils as ut
    from . import settings as st


# ##############################################################################
def plot_graph_runtime(data, 
                       x_axis, x_label, x_ticks, x_tick_labels, x_scale,
                       y_axis, y_label, line_color, line_style, legend_title, 
                       title, fname_path):
  # --------------------------------------------------------------------------
  # general settings
  ## dark or white grid
  # sb.set_style('darkgrid')
  sb.set_style('whitegrid')

  # --------------------------------------------------------------------------
  # 📊 plot 
  # fig = plt.figure(figsize=(16,9))
  fig = plt.figure()
  g = sb.lineplot(data=data, x=x_axis, y=y_axis, 
                  hue=line_color, style=line_style,
                  marker='o', dashes=True,
                  )

  # title = None
  ## graph-specific tweaks
  ### scaling & title
  g.set_xscale(x_scale)
  if (title==None):
    plt.tight_layout()
  else:
    # plt.tight_layout(rect=(0,0,1,.93)) # rect=(left, bottom, right, top); default: (0,0,1,1)
    plt.tight_layout(rect=(0,0,1,.90)) # rect=(left, bottom, right, top); default: (0,0,1,1)
    g.set_title(title, fontsize=13, fontstyle='oblique')

  ### labels
  g.set_ylabel(y_label, fontsize=13, fontstyle='oblique')
  g.set_xlabel(x_label, fontsize=13, fontstyle='oblique')
  if (x_tick_labels != None):
    g.set_xticks(x_ticks, labels=x_tick_labels)
  g.tick_params(labelsize=13)


  # new_legend_labels = ['Engine', 'natSPDZ', 'webSPDZ']
  new_legend_labels = None
  if (new_legend_labels is not None):
    leg = g.get_legend()
    for t, l in zip(leg.texts, new_legend_labels):
      t.set_text(l)

  ### positioning (legend/..)
  plt.legend(fontsize=13, title=legend_title, title_fontsize=13)
  # base_legend_position = (0.3, 0.7)
  base_legend_position = None
  if base_legend_position is not None:
    # leg.set_bbox_to_anchor(base_legend_position)
    plt.legend(bbox_to_anchor=base_legend_position, ncol=1,
              borderaxespad=0., fontsize=13, title=legend_title, title_fontsize=13
              )  

  # --------------------------------------------------------------------------
  # 💽 store graph
  fig.savefig(fname_path)

  # --------------------------------------------------------------------------
  # 🧼 cleanup
  plt.close('all')

# ##############################################################################
def create_graph_runtime(bms, nr_runs, program, x_axis, x_label, 
                         graph_dir, graph_title,
                         line_color=None, line_style=None, legend_title='Legend'):
  view_data = []

  # (0) extract relevant bench. data
  # TODO: craft BM class for this (as in b4M)
  for iteration in bms:
    prog_iter=iteration[0] # TODO: activate program
    nr_parties=iteration[1]
    arr_length=iteration[2]
    proto_id=iteration[3]
    eng=iteration[4]
    network=iteration[5]

    proto = ut.PROTO_MAP[proto_id]
    # --------------------------------------------------------------------------
    # General data
    view_ele={
      'Program': program,
      'Engine': eng,
      'Network': network.upper(),
      'Protocol': proto,
      '#Parties': nr_parties,
      '#Eles': arr_length,
    }

    # --------------------------------------------------------------------------
    # Timings
    fname = ut.get_json_file_name(prog=program, engine=eng, protocol=proto, network=network,
                                  nr_parties=nr_parties, arr_length=arr_length, nr_runs=nr_runs)
    # print("fname: ", fname)
    data_bench = ut.read_in_json(eng, program, fname)
    timings_avg = data_bench['timings']['avg']
    view_ele['runtime-avg-full'] = max(timings_avg['full'])
    view_ele['runtime-avg-input'] = max(timings_avg['input'])
    view_ele['runtime-avg-computation'] = max(timings_avg['computation'])
    # view_ele['runtime-avg-ML-train'] = max(timings_avg['ML-train'])
    # view_ele['runtime-avg-ML-predict'] = max(timings_avg['ML-predict'])

    # TODO: std. deviation of all runs / other parties ?

    ## modify-engine hack for the webSPDZ paper ^^
    ## ...after reading in the file
    if (eng=='mpSPDZ'): view_ele['Engine']='natSPDZ'

    view_data.append(view_ele)
  # end-for: bms

  # (1) convert JSON view data to Pandas data frame
  df = pd.DataFrame(view_data)
  ut.print_debug("data frame:\n" + str(df), 1)

  # (2) plot data
  # seconds
  for timer in st.TIMERS: 
    y_axis = timer['Y-axis']
    runtime_unit = 's' # seconds
    y_label = timer['Y-label'] % runtime_unit
    # TODO: graph object with general settings; such as x_axis, x_label, etc. :D

    proto = '-'.join([ut.PROTO_MAP[p_id] for p_id in st.PROTOCOLS])
    network = 'LAN'

    ## setting line color & style
    if (line_color==None): line_color = 'Engine'
    if (line_style==None): line_style = 'Protocol'

    prog = program.replace(' ','-').lower()
    nr_p = nr_parties
    nr_eles = arr_length

    t_id = timer['id'].replace('_','-')

    if (x_axis=='#Eles'):
      graph_fname = f'runtime-{t_id}_{prog}_{proto}_{nr_p}P_{network}_X-eles'
      # graph_fname = f'runtime-{t_id}_{prog}_{proto}_{nr_p}P_{network}_X-eles'
      # TODO: move to settings! :)
      if ('BB-' in program):
        x_scale='log'
        x_ticks=None
        x_tick_labels=None
      elif ('LogReg' in program):
        x_scale='linear'
        x_ticks=st.ARRAY_LENGTHS
        x_tick_labels = [str(ele) for ele in st.ARRAY_LENGTHS]
      else:
        raise NotImplementedError('no scale/ticks for %s defined' % program)
    elif (x_axis=='#Parties'):
      graph_fname = f'runtime-{t_id}_{prog}_{proto}_{nr_eles}eles_{network}_X-parties'
      x_scale='linear'
      x_ticks=st.NR_PLAYERS
      x_tick_labels = [str(p) for p in st.NR_PLAYERS]
    else:
      print("Unsupported X-axis: ", x_axis)
      sys.exit(-1)

    title = graph_title % timer['title']
    graph_path = os.path.join(graph_dir, graph_fname+'.pdf')
    plot_graph_runtime(data=df, 
                       x_axis=x_axis, x_label=x_label, x_ticks=x_ticks, x_tick_labels=x_tick_labels, x_scale=x_scale,
                       y_axis=y_axis, y_label=y_label, 
                       line_color=line_color, line_style=line_style, legend_title=legend_title, 
                       title=title, fname_path=graph_path,
                      )

