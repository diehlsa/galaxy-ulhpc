# A simple CLI runner for OAR that can be used when running Galaxy from a
# non-submit host and using a OAR cluster.

# OAR job states:
#
#                 'Waiting' => 'W',
#                 'toLaunch' => 'L',
#                 'Launching' => 'L',
#                 'Hold'        => 'H',
#                 'Running' => 'R',
#                 'Terminated' => 'T',
#                 'Error' => 'E',
#                 'toError' => 'E',
#                 'Finishing' => 'F',
#                 'Suspended' => 'S',
#                 'Resuming' => 'S',
#                 'toAckReservation' => 'W'


try:
    from galaxy.model import Job
    job_states = Job.states
except ImportError:
    # Not in Galaxy, map Galaxy job states to Pulsar ones.
    from galaxy.util import enum
    job_states = enum(RUNNING='running', OK='complete', QUEUED='queued')

from ..job import BaseJobExec

__all__ = ('Oar',)

from logging import getLogger
log = getLogger(__name__)

from galaxy import eggs
eggs.require('PyYaml')
import yaml

argmap = {
    'resources': '-l',
    'properties': '-p',
}


class Oar(BaseJobExec):

    def __init__(self, **params):
        self.params = {}
        for k, v in params.items():
            self.params[k] = v

    def job_script_kwargs(self, ofile, efile, job_name):
        scriptargs = {'-O ': ofile,
                      '-E ': efile,
                      '-n ': job_name}

        # Map arguments using argmap.
        for k, v in self.params.items():
            if k == 'plugin':
                continue
            try:
                if not k.startswith('-'):
                    k = argmap[k]
                scriptargs[k] = v
            except:
                log.warning('Unrecognized long argument passed to OAR CLI plugin: %s' % k)

        # Generated template.
        template_scriptargs = ''
        for k, v in scriptargs.items():
            template_scriptargs += '#OAR %s%s\n' % (k, v)
        return dict(headers=template_scriptargs)

    def submit(self, script_file):
        return 'oarsub -S %s' % script_file

    def delete(self, job_id):
        return 'oardel %s' % job_id

    def get_status(self, job_ids=None):
        return 'oarstat -Y'

    def get_single_status(self, job_id):
        return 'oarstat -Y -s -j %s' % job_id

    def parse_status(self, status, job_ids):
        # Get status for each job, skipping header.
        rval = {}
        status = yaml.load(status)
        for id in status:
            state = status[id]['state']
            if str(id) in job_ids: 
                rval[str(id)] = self._get_job_state(state)
        return rval

    def parse_single_status(self, status, job_id):
        status = yaml.load(status)
        if status is not None:
            return self._get_job_state(status[int(job_id)])
        return job_states.OK

    def _get_job_state(self, state):
        try:
            return {
                'Waiting': job_states.QUEUED,
                'toLaunch': job_states.QUEUED,
                'Launching': job_states.QUEUED,
                'Hold': job_states.WAITING,
                'Running': job_states.RUNNING,
                'Terminated': job_states.OK,
                'Error': job_states.ERROR,
                'toError': job_states.ERROR,
                'Finishing': job_states.RUNNING,
                'Suspended': job_states.PAUSED,
                'Resuming': job_states.PAUSED,
                'toAckReservation': job_states.NEW
            }.get(state)
        except KeyError:
            raise KeyError("Failed to map OAR status [%s] to job state." % state)


