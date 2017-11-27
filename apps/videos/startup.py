from django.utils.translation import ugettext_lazy as _

import videos.signalhandlers
import staff

staff.register(_('Amara On-Demand'), _('Video URL Search'),
               'videos:url-search')
