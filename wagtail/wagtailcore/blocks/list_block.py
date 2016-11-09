from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.forms.utils import ErrorList
from django.template.loader import render_to_string
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from wagtail.wagtailcore.utils import escape_script

from .base import Block
from .utils import js_dict

__all__ = ['ListBlock', 'ListBlockValidationError']


class ListBlockValidationError(ValidationError):
    def __init__(self, block_errors=None, non_block_errors=None):
        params = {}
        if block_errors:
            params.update(block_errors)
        if non_block_errors:
            params[NON_FIELD_ERRORS] = non_block_errors
        super(ListBlockValidationError, self).__init__(
            'Validation error in ListBlock', params=params)


class ListBlock(Block):

    def __init__(self, child_block, max_length=None, min_length=None, **kwargs):
        self.list_options = {
            'max_length': max_length,
            'min_length': min_length
        }
        super(ListBlock, self).__init__(**kwargs)

        if isinstance(child_block, type):
            # child_block was passed as a class, so convert it to a block instance
            self.child_block = child_block()
        else:
            self.child_block = child_block

        if not hasattr(self.meta, 'default'):
            # Default to a list consisting of one empty (i.e. default-valued) child item
            self.meta.default = [self.child_block.get_default()]

        self.dependencies = [self.child_block]
        self.child_js_initializer = self.child_block.js_initializer()

    @property
    def media(self):
        return forms.Media(js=[static('wagtailadmin/js/blocks/sequence.js'), static('wagtailadmin/js/blocks/list.js')])

    def render_list_member(self, value, prefix, index, errors=None):
        """
        Render the HTML for a single list item in the form. This consists of an <li> wrapper, hidden fields
        to manage ID/deleted state, delete/reorder buttons, and the child block's own form HTML.
        """
        child = self.child_block.bind(value, prefix="%s-value" % prefix, errors=errors)
        return render_to_string('wagtailadmin/block_forms/list_member.html', {
            'prefix': prefix,
            'child': child,
            'index': index,
        })

    def html_declarations(self):
        # generate the HTML to be used when adding a new item to the list;
        # this is the output of render_list_member as rendered with the prefix '__PREFIX__'
        # (to be replaced dynamically when adding the new item) and the child block's default value
        # as its value.
        list_member_html = self.render_list_member(self.child_block.get_default(), '__PREFIX__', '')

        return format_html(
            '<script type="text/template" id="{0}-newmember">{1}</script>',
            self.definition_prefix, mark_safe(escape_script(list_member_html))
        )

    def js_initializer(self):
        opts = {'definitionPrefix': "'%s'" % self.definition_prefix}

        if self.child_js_initializer:
            opts['childInitializer'] = self.child_js_initializer

        return "ListBlock(%s)" % js_dict(opts)

    def render_form(self, value, prefix='', errors=None):
        error_dict = {}
        if errors:
            if len(errors) > 1:
                # We rely on ListBlock.clean throwing a single ListBlockValidationError with a specially crafted
                # 'params' attribute that we can pull apart and distribute to the child blocks
                raise TypeError('ListBlock.render_form unexpectedly received multiple errors')
            error_dict = errors.as_data()[0].params

        list_members_html = [
            self.render_list_member(child_val, "%s-%d" % (prefix, i), i,
                                    errors=error_dict.get(i))
            for (i, child_val) in enumerate(value)
        ]

        return render_to_string('wagtailadmin/block_forms/list.html', {
            'help_text': getattr(self.meta, 'help_text', None),
            'prefix': prefix,
            'list_members_html': list_members_html,
            'block_errors': error_dict.get(NON_FIELD_ERRORS),
        })

    def value_from_datadict(self, data, files, prefix):
        count = int(data['%s-count' % prefix])
        values_with_indexes = []
        for i in range(0, count):
            if data['%s-%d-deleted' % (prefix, i)]:
                continue
            values_with_indexes.append(
                (
                    int(data['%s-%d-order' % (prefix, i)]),
                    self.child_block.value_from_datadict(data, files, '%s-%d-value' % (prefix, i))
                )
            )

        values_with_indexes.sort()
        return [v for (i, v) in values_with_indexes]

    def value_omitted_from_data(self, data, files, prefix):
        return ('%s-count' % prefix) not in data

    def clean(self, value):
        result = []
        errors = {}
        for i, child_val in enumerate(value):
            try:
                result.append(self.child_block.clean(child_val))
            except ValidationError as e:
                errors[i] = ErrorList([e])

        max_length = self.list_options['max_length']
        if max_length and max_length < len(value):
            raise ListBlockValidationError(non_block_errors=ErrorList([
                ValidationError(_("Maximum of %s is reached" % max_length))]))

        min_length = self.list_options['min_length']
        if min_length and min_length > len(value):
            raise ListBlockValidationError(non_block_errors=ErrorList([
                ValidationError(_("Minimum of %s is required" % min_length))]))

        if errors:
            # The message here is arbitrary - outputting error messages is delegated to the child blocks,
            # which only involves the 'params' list
            raise ListBlockValidationError(block_errors=errors)

        return result

    def to_python(self, value):
        # recursively call to_python on children and return as a list
        return [
            self.child_block.to_python(item)
            for item in value
        ]

    def get_prep_value(self, value):
        # recursively call get_prep_value on children and return as a list
        return [
            self.child_block.get_prep_value(item)
            for item in value
        ]

    def render_basic(self, value, context=None):
        children = format_html_join(
            '\n', '<li>{0}</li>',
            [
                (self.child_block.render(child_value, context=context),)
                for child_value in value
            ]
        )
        return format_html("<ul>{0}</ul>", children)

    def get_searchable_content(self, value):
        content = []

        for child_value in value:
            content.extend(self.child_block.get_searchable_content(child_value))

        return content

    def check(self, **kwargs):
        errors = super(ListBlock, self).check(**kwargs)
        errors.extend(self.child_block.check(**kwargs))
        return errors

    class Meta:
        # No icon specified here, because that depends on the purpose that the
        # block is being used for. Feel encouraged to specify an icon in your
        # descendant block type
        icon = "placeholder"


DECONSTRUCT_ALIASES = {
    ListBlock: 'wagtail.wagtailcore.blocks.ListBlock',
}
