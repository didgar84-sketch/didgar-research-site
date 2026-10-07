"""Normal-model TOST teaching example, not a design-specific trial analysis.

The supplied SE must be known or justified by a suitable large-sample model.
Bounds have the estimate's units and must be justified before seeing results.
"""
from statistics import NormalDist
import math


def tost_normal(estimate, standard_error, lower, upper, alpha=0.05):
    values=(estimate, standard_error, lower, upper, alpha)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError('All inputs must be finite.')
    if standard_error<=0 or lower>=upper or not 0<alpha<0.5:
        raise ValueError('Require SE>0, lower<upper and 0<alpha<0.5.')
    normal=NormalDist()
    p_lower=1-normal.cdf((estimate-lower)/standard_error)
    p_upper=normal.cdf((estimate-upper)/standard_error)
    z_equiv=normal.inv_cdf(1-alpha)
    z_difference=normal.inv_cdf(1-alpha/2)
    return {
        'model':'normal, justified known or large-sample standard error',
        'estimate':estimate, 'standard_error':standard_error,
        'bounds':[lower,upper], 'alpha':alpha,
        'p_lower':p_lower, 'p_upper':p_upper, 'p_tost':max(p_lower,p_upper),
        'equivalent':max(p_lower,p_upper)<alpha,
        'equivalence_interval':[estimate-z_equiv*standard_error,estimate+z_equiv*standard_error],
        'difference_interval':[estimate-z_difference*standard_error,estimate+z_difference*standard_error],
        'different_from_zero':2*(1-normal.cdf(abs(estimate/standard_error)))<alpha,
        'status':'synthetic numerical teaching scenario; not estimated from synthetic.csv'
    }


def teaching_scenarios():
    return [tost_normal(0.2,se,-0.5,0.5) for se in (0.15,1.0)]


if __name__=='__main__':
    import json
    print(json.dumps(teaching_scenarios(),ensure_ascii=False,indent=2))
