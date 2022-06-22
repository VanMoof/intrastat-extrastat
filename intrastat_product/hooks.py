# Copyright 2022 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging


def pre_init_hook(cr):
    """Prepopulate stored computed fields for faster installation"""
    logger = logging.getLogger(__name__)
    logger.info("Prepopulating stored computed fields")
    cr.execute(
        """
        alter table account_invoice
        add column if not exists src_dest_country_id integer,
        add column if not exists intrastat_country boolean;
        """)
    cr.execute(
        """
        with countries as (
            select ai.id as invoice_id,
            rco.id as country_id,
            rco.intrastat
            from account_invoice ai
            left join res_partner rps on rps.id = ai.partner_shipping_id
            join res_partner rp on rp.id = ai.partner_id
            join res_company rc on rc.id = ai.company_id
            join res_partner rpc on rpc.id = rc.partner_id
            join res_country rco
                on rco.id = coalesce(
                    rps.country_id,
                    rp.country_id,
                    rpc.country_id
                )
        )
        update account_invoice ai
        set src_dest_country_id = countries.country_id,
            intrastat_country = countries.intrastat
        from countries where ai.id = countries.invoice_id;
        """)
