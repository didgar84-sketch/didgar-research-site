"""Reproducible synthetic teaching pipeline, using only the Python standard library.

Six paths = three illustrative quality rules x two OLS specifications. The
coefficients are descriptive; there are no confidence intervals, valid curve
inference, power claims or causal conclusions. This is not JOSS-ready software.
"""
from pathlib import Path
from statistics import fmean, stdev
import argparse, csv, hashlib, html, json, math
from equivalence import teaching_scenarios

ROOT=Path(__file__).resolve().parent
FIELDS=('participant_id','study_hours','baseline','score','quality_flag')


def load_data(filename):
    with Path(filename).open(newline='',encoding='utf-8') as handle:
        reader=csv.DictReader(handle)
        if tuple(reader.fieldnames or ())!=FIELDS:
            raise ValueError('The CSV columns must match the documented dictionary.')
        rows=[]; identifiers=set()
        for line,row in enumerate(reader,2):
            identifier=row['participant_id']
            if not identifier or identifier in identifiers:
                raise ValueError(f'Empty or duplicate ID at line {line}.')
            identifiers.add(identifier)
            parsed={'participant_id':identifier,'quality_flag':row['quality_flag']}
            if parsed['quality_flag'] not in ('none','A','B'):
                raise ValueError(f'Unknown quality flag at line {line}.')
            for field,upper in (('study_hours',24),('baseline',100),('score',100)):
                try: number=float(row[field])
                except (TypeError,ValueError): raise ValueError(f'Invalid numeric {field} at line {line}.') from None
                if not math.isfinite(number) or not 0<=number<=upper:
                    raise ValueError(f'Out-of-range {field} at line {line}.')
                parsed[field]=number
            rows.append(parsed)
    if len(rows)<3: raise ValueError('At least three teaching records are required.')
    return rows


def fit_ols(rows,adjusted=False):
    """Closed-form OLS for score ~ hours (+ baseline), with a fitted intercept."""
    if len(rows)<3: raise ValueError('At least three records are required.')
    xbar=fmean(r['study_hours'] for r in rows)
    ybar=fmean(r['score'] for r in rows)
    zbar=fmean(r['baseline'] for r in rows)
    sxx=sum((r['study_hours']-xbar)**2 for r in rows)
    sxy=sum((r['study_hours']-xbar)*(r['score']-ybar) for r in rows)
    if sxx<=0: raise ValueError('Study hours must vary.')
    beta_z=None
    if adjusted:
        szz=sum((r['baseline']-zbar)**2 for r in rows)
        sxz=sum((r['study_hours']-xbar)*(r['baseline']-zbar) for r in rows)
        szy=sum((r['baseline']-zbar)*(r['score']-ybar) for r in rows)
        determinant=sxx*szz-sxz*sxz
        if abs(determinant)<=1e-12*max(1,sxx*szz):
            raise ValueError('The adjusted design is singular or numerically unsuitable.')
        beta_x=(sxy*szz-szy*sxz)/determinant
        beta_z=(szy*sxx-sxy*sxz)/determinant
    else: beta_x=sxy/sxx
    intercept=ybar-beta_x*xbar-(beta_z*zbar if adjusted else 0)
    residual=sum((r['score']-intercept-beta_x*r['study_hours']-(beta_z*r['baseline'] if adjusted else 0))**2 for r in rows)
    total=sum((r['score']-ybar)**2 for r in rows)
    return {'n':len(rows),'intercept':intercept,'beta_hours':beta_x,
            'beta_baseline':beta_z,'r_squared':1-residual/total if total else None}


def analysis_paths(rows):
    paths=[]
    for rule,rejected in (('all',()),('exclude_A',('A',)),('exclude_A_B',('A','B'))):
        selected=[r for r in rows if r['quality_flag'] not in rejected]
        for adjusted in (False,True):
            paths.append({'quality_rule':rule,'specification':'baseline_adjusted' if adjusted else 'unadjusted',
                          **fit_ols(selected,adjusted)})
    return paths


def specification_svg(paths):
    """An original data chart; descriptive paths, no inferential error bars."""
    values=[p['beta_hours'] for p in paths]
    low=min(0,min(values)-0.2); high=max(0,max(values)+0.2)
    scale=lambda value:420+(value-low)/(high-low)*470
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 560" role="img" aria-labelledby="title description">',
           '<title id="title">Six descriptive paths on synthetic data</title>',
           '<desc id="description">OLS coefficients for study hours under three illustrative quality rules and two specifications. No real participants, confidence intervals or causal claims.</desc>',
           '<rect width="960" height="560" fill="#f8fafb"/>',
           '<g font-family="Arial,sans-serif" fill="#122d40"><text x="36" y="45" font-size="24">Six descriptive paths · synthetic teaching data</text>',
           '<text x="36" y="76" font-size="15">Point estimates only; choices are illustrative, not a validated specification-curve test.</text>']
    for i in range(5):
        value=low+(high-low)*i/4; position=scale(value)
        parts.append(f'<line x1="{position:.3f}" x2="{position:.3f}" y1="110" y2="450" stroke="#dbe3e9"/><text x="{position:.3f}" y="480" font-size="14" text-anchor="middle">{value:.2f}</text>')
    for i,path in enumerate(paths):
        y=130+i*55; color='#725221' if path['specification']=='baseline_adjusted' else '#123349'
        label=f'{path["quality_rule"]} / {path["specification"]} (n={path["n"]})'
        parts.append(f'<text x="36" y="{y+5}" font-size="15">{html.escape(label)}</text><circle cx="{scale(path["beta_hours"]):.3f}" cy="{y}" r="7" fill="{color}"/><text x="915" y="{y+5}" font-size="14" text-anchor="end">{path["beta_hours"]:.3f}</text>')
    parts.append('<text x="650" y="520" text-anchor="middle" font-size="17">Score points per study hour (OLS coefficient)</text></g></svg>')
    return ''.join(parts)


def run_project(datafile=ROOT/'synthetic.csv',output=ROOT/'outputs'):
    rows=load_data(datafile);paths=analysis_paths(rows)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    summary={'project_version':'1.0.0','status':'entirely synthetic teaching data',
             'n':len(rows),'mean_score':fmean(r['score'] for r in rows),
             'sd_score':stdev(r['score'] for r in rows),
             'source_sha256':hashlib.sha256(Path(datafile).read_bytes()).hexdigest(),
             'analysis_paths':len(paths),'coefficient_units':'score points per study hour',
             'limitations':'Descriptive OLS examples; no inference, causality or real-population estimates.'}
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (output/'paths.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(paths[0]));writer.writeheader();writer.writerows(paths)
    svg=specification_svg(paths);(output/'specification.svg').write_text(svg,encoding='utf-8')
    (output/'equivalence.json').write_text(json.dumps(teaching_scenarios(),indent=2)+'\n',encoding='utf-8')
    table=''.join('<tr>'+''.join('<td>'+html.escape(str(p[k]))+'</td>' for k in ('quality_rule','specification','n'))+f'<td>{p["beta_hours"]:.6f}</td></tr>' for p in paths)
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Synthetic research pipeline output</title><style>body{font:17px/1.7 Arial,sans-serif;color:#122d40;background:#f8fafb;max-width:1100px;margin:auto;padding:25px}svg{width:100%;height:auto}table{border-collapse:collapse;width:100%}th,td{border:1px solid #718796;padding:10px;text-align:left}.scroll{overflow:auto}.note{padding:18px;background:#eee7db}</style><h1>Synthetic research pipeline</h1><p class="note">Teaching data only. No actual participants or empirical findings. OLS paths are descriptive; the separate normal-model TOST numbers are not calculated from this dataset.</p>'+f'<p>Records: {summary["n"]}; mean score: {summary["mean_score"]:.3f}; sample SD: {summary["sd_score"]:.3f}.</p>'+svg+'<div class="scroll"><table><caption>All six illustrative paths</caption><thead><tr><th scope="col">Quality rule</th><th scope="col">Specification</th><th scope="col">n</th><th scope="col">Hours coefficient</th></tr></thead><tbody>'+table+'</tbody></table></div><p>File SHA-256: <code>'+summary['source_sha256']+'</code></p></html>'
    (output/'index.html').write_text(document,encoding='utf-8')
    return {'summary':summary,'paths':paths}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=ROOT/'synthetic.csv')
    parser.add_argument('--output',type=Path,default=ROOT/'outputs')
    args=parser.parse_args()
    print(json.dumps(run_project(args.data,args.output)['summary'],indent=2))
