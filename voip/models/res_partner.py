# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from playsound import playsound

import logging

_logger = logging.getLogger(__name__)

global _phonenumbers_lib_warning
_phonenumbers_lib_warning = False

global _phonenumbers_lib_imported
_phonenumbers_lib_imported = False

try:
    import phonenumbers

    _phonenumbers_lib_imported = True

except ImportError:

    if not _phonenumbers_lib_warning:
        _logger.warning("The `phonenumbers` Python module is not installed, contact look up will not be "
                        "done for incoming calls. Try: pip install phonenumbers.")
        _phonenumbers_lib_warning = True


class Contact(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.validation.mixin']

    sanitized_phone = fields.Char("Phone number sanitized", compute='_compute_sanitized_phone', store=True)
    sanitized_mobile = fields.Char("Mobile number sanitized", compute='_compute_sanitized_mobile', store=True)

    def _voip_sanitization(self, number):
        if _phonenumbers_lib_imported:
            country = self._phone_get_country()
            country_code = country.code if country else None
            try:
                phone_nbr = phonenumbers.parse(number, region=country_code, keep_raw_input=True)
            except phonenumbers.phonenumberutil.NumberParseException:
                return number
            if not phonenumbers.is_possible_number(phone_nbr) or not phonenumbers.is_valid_number(phone_nbr):
                return number
            phone_fmt = phonenumbers.PhoneNumberFormat.INTERNATIONAL
            return phonenumbers.format_number(phone_nbr, phone_fmt).replace(' ', '')
        else:
            return number

    @api.multi
    @api.depends('phone', 'country_id')
    def _compute_sanitized_phone(self):
        for partner in self:
            if partner.phone:
                partner.sanitized_phone = partner._voip_sanitization(partner.phone)

    @api.multi
    @api.depends('mobile', 'country_id')
    def _compute_sanitized_mobile(self):
        for partner in self:
            if partner.mobile:
                partner.sanitized_mobile = partner._voip_sanitization(partner.mobile)


class Partner(models.Model):
    _inherit = 'res.partner'

    audio_url = fields.Char(string='Audio')