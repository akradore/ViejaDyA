# See LICENSE file for full copyright and licensing details.
"""Label Print Wizard Model."""

from odoo import fields, models, api, _
from odoo.tools import ustr
from PIL import Image
import codecs
import base64
import shutil
import os
import io


class WizExportZip(models.TransientModel):
    """Export Zip."""

    _name = 'wiz.export.zip'
    _description = "Wizard Export Zip"

    name = fields.Char(string="Name")
    file = fields.Binary(string="File")


class WizExportImage(models.TransientModel):
    """Label Print Wizard Model."""

    _name = 'wiz.export.image'
    _description = "Wizard Export Image"

    product_temp_ids = fields.Many2many('product.template',
                                        'exp_image_product_temp_rel',
                                        'export_id', 'product_id',
                                        string="Products")
    product_ids = fields.Many2many('product.product',
                                   'exp_image_product_rel',
                                   'export_id', 'product_id',
                                   string="Products")
    location = fields.Char(string="Location")
    zip_name = fields.Char(string="Zip Name")
    img_size = fields.Selection([
        ('image', 'Large'), ('image_medium', 'Medium'),
        ('image_small', 'Small')], string="Image Size",
        default="image_medium")

    @api.multi
    def export_image(self):
        """Export Product Images."""
        self.ensure_one()
        zip_name = self.zip_name + '.zip'
        location = ustr(self.location) + ustr('export_image')
        zip_nm = ustr(self.location) + ustr(self.zip_name)
        modid = self.env['ir.model.data'].get_object_reference(
            'scs_product_image_export', 'view_wiz_export_zip')
        products = []
        if self._context.get('active_model', False):
            if self._context.get('active_model') == 'product.template':
                products = self.product_temp_ids
            elif self._context.get('active_model') == 'product.product':
                products = self.product_ids
        if not os.path.isdir(location):
            os.mkdir(location)
        for pro in products:
            if self.img_size == 'image':
                data = pro.image
            elif self.img_size == 'image_small':
                data = pro.image_small
            else:
                data = pro.image_medium
            if data:
                image_stream = io.BytesIO(codecs.decode(data, 'base64'))
                image = Image.open(image_stream)
                fname = (pro.default_code and (pro.default_code + "_") or "") \
                    + pro.name.replace(' ', '_') + '.' + image.format
                # fname = pro.name + '.' + image.format
                product_img = base64.decodestring(data)
                fp = open(os.path.join(location, fname), 'wb')
                fp.write(product_img)
                fp.close()
        img_zip = shutil.make_archive(zip_nm, 'zip', location)
        read_zip = base64.b64encode(open(img_zip, 'rb').read())
        res_id = self.env['wiz.export.zip'].create(
            {
                'name': zip_name or '',
                'file': read_zip
            }).id
        if os.path.isdir(location):
            shutil.rmtree(location, ignore_errors=False, onerror=None)
            os.remove(img_zip)
        return {
            'name': _('Download Zip File'),
            'view_mode': 'form',
            'view_id': modid[1],
            'view_type': 'form',
            'res_model': 'wiz.export.zip',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': res_id,
        }

    @api.model
    def default_get(self, default_fields):
        """Base default get method."""
        res = super(WizExportImage, self).default_get(default_fields)
        # path = ustr("c:\\tmp\\")
        path = os.path.join('c:', 'tmp', '')
        if os.sys.platform.startswith('linux'):
            path = ustr('/tmp/')
        else:
            tmp_dir = os.path.join('c:', 'tmp')
            if not os.path.isdir(tmp_dir):
                os.mkdir(tmp_dir)
        res.update({'zip_name': 'product_images',
                    'location': path})
        if self._context.get('active_model', False):
            if self._context.get('active_model') == 'product.template':
                res.update({'product_temp_ids':
                            [(6, 0, self._context.get('active_ids', []))]})
            elif self._context.get('active_model') == 'product.product':
                res.update({'product_ids':
                            [(6, 0, self._context.get('active_ids', []))]})
        return res
