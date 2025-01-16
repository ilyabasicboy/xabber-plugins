from django.http import HttpResponse
from django.views import View
import xml.etree.ElementTree as ET
from xabber_plugins.plugins.models import Plugin


class PluginListApi(View):

    def get(self, request, *args, **kwargs):
        plugins = Plugin.objects.all()

        name = request.GET.get('name')
        if name:
            plugins = plugins.filter(name=name)

        xabber_server_version = request.GET.get('xabber_server_version')

        # Start building the XML response
        response_element = ET.Element('response')

        for plugin in plugins:
            developer = plugin.developer  # Assuming each plugin has a related developer

            if xabber_server_version:
                release = plugin.release_set.filter(xabber_server_versions__contains=[xabber_server_version]).order_by('version').last()
            else:
                release = plugin.release_set.order_by('version').last()

            plugin_data = {
                'name': plugin.name,
                'display_name': plugin.display_name,
                'developer_name': developer.username,
                'developer_email': developer.email,
                'developer_contacts': developer.contacts,
                'developer_site': developer.site,
                'release': release.version if release else None,
                'download': f'{request.scheme}://{request.get_host()}{release.file.url}'
            }

            plugin_element = ET.SubElement(response_element, 'plugin')

            for key, value in plugin_data.items():
                sub_element = ET.SubElement(plugin_element, key)
                sub_element.text = str(value) if value else ''

            # Adding descriptions with the language attribute
            descriptions = plugin.descriptions.all()
            for description in descriptions:
                description_element = ET.SubElement(plugin_element, 'description', language=description.language)
                description_element.text = description.description

        # Convert the tree to a byte string
        xml_data = ET.tostring(response_element, encoding='utf-8', method='xml')

        # Return the response as XML
        return HttpResponse(xml_data, content_type='application/xml')
