def setup_logger(ignore_errors):
    if ignore_errors == 2:
        logging.basicConfig(filename='/tmp/xbrl.log',
            level=logging.ERROR,
            format='%(asctime)s %(levelname)s %(name)s %(message)s')
        return logging.getLogger(__name__)
    else:
        return None

class PlaceHolder(object):
    @classmethod
    def parseGAAP(self,
                  xbrl,
                  doc_date="",
                  context="current",
                  ignore_errors=0):
        """
        Parse GAAP from our XBRL soup and return a GAAP object.
        """
        gaap_obj = GAAP()

        logger = setup_logger(ignore_errors)

        # the default is today
        if doc_date == "":
            doc_date = str(datetime.date.today())
        doc_date = re.sub(r"[^0-9]+", "", doc_date)

        # current is the previous quarter
        if context == "current":
            context = 90

        if context == "year":
            context = 360

        context = int(context)

        if context % 90 == 0:
            context_extended = list(range(context, context + 9))
            expected_start_date = (
                datetime.datetime.strptime(doc_date, "%Y%m%d") 
                - datetime.timedelta(days=context)
            )
        elif context == "instant":
            expected_start_date = None
        else:
            raise XBRLParserException('invalid context')

        # we need expected end date unless instant
        if context != "instant":
            expected_end_date = \
                datetime.datetime.strptime(doc_date, "%Y%m%d")

        doc_root = ""

        # we might need to attach the document root
        if len(self.xbrl_base) > 1:
            doc_root = self.xbrl_base

        # collect all contexts up that are relevant to us
        # TODO - Maybe move this to Preprocessing Ingestion
        context_ids = []
        context_tags = xbrl.find_all(name=re.compile(doc_root + "context",
                                     re.IGNORECASE | re.MULTILINE))

        try:
            for context_tag in context_tags:
                # we don't want any segments
                if context_tag.find(doc_root + "entity") is None:
                    continue
                if context_tag.find(doc_root + "entity").find(
                doc_root + "segment") is None:
                    context_id = context_tag.attrs['id']

                    found_start_date = None
                    found_end_date = None

                    if context_tag.find(doc_root + "instant"):
                        instant = \
                            datetime.datetime.strptime(re.compile('[^\d]+')
                                                       .sub('', context_tag
                                                       .find(doc_root +
                                                             "instant")
                                                        .text)[:8], "%Y%m%d")
                        if instant == expected_end_date:
                            context_ids.append(context_id)
                            continue

                    if context_tag.find(doc_root + "period").find(
                    doc_root + "startdate"):
                        found_start_date = \
                            datetime.datetime.strptime(re.compile('[^\d]+')
                                                       .sub('', context_tag
                                                       .find(doc_root +
                                                             "period")
                                                       .find(doc_root +
                                                             "startdate")
                                                        .text)[:8], "%Y%m%d")
                    if context_tag.find(doc_root + "period").find(doc_root +
                    "enddate"):
                        found_end_date = \
                            datetime.datetime.strptime(re.compile('[^\d]+')
                                                       .sub('', context_tag
                                                       .find(doc_root +
                                                             "period")
                                                       .find(doc_root +
                                                             "enddate")
                                                       .text)[:8], "%Y%m%d")
                    if found_end_date and found_start_date:
                        for ce in context_extended:
                            if found_end_date - found_start_date == \
                            datetime.timedelta(days=ce):
                                if found_end_date == expected_end_date:
                                    context_ids.append(context_id)
        except IndexError:
            raise XBRLParserException('problem getting contexts')

        assets = xbrl.find_all("us-gaap:assets")
        gaap_obj.assets = self.data_processing(assets, xbrl,
            ignore_errors, logger, context_ids)

        current_assets = \
            xbrl.find_all("us-gaap:assetscurrent")
        gaap_obj.current_assets = self.data_processing(current_assets,
            xbrl, ignore_errors, logger, context_ids)

        non_current_assets = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(assetsnoncurrent)",
                          re.IGNORECASE | re.MULTILINE))
        if non_current_assets == 0 or not non_current_assets:
            # Assets  = AssetsCurrent  +  AssetsNoncurrent
            gaap_obj.non_current_assets = gaap_obj.assets \
                - gaap_obj.current_assets
        else:
            gaap_obj.non_current_assets = \
                self.data_processing(non_current_assets, xbrl,
                    ignore_errors, logger, context_ids)

        liabilities_and_equity = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(liabilitiesand)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.liabilities_and_equity = \
            self.data_processing(liabilities_and_equity, xbrl,
                ignore_errors, logger, context_ids)

        liabilities = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(liabilities)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.liabilities = \
            self.data_processing(liabilities, xbrl, ignore_errors,
                logger, context_ids)

        current_liabilities = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]\
                          *(currentliabilities)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.current_liabilities = \
            self.data_processing(current_liabilities, xbrl,
                ignore_errors, logger, context_ids)

        noncurrent_liabilities = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]\
                          *(noncurrentliabilities)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.noncurrent_liabilities = \
            self.data_processing(noncurrent_liabilities, xbrl,
                ignore_errors, logger, context_ids)

        commitments_and_contingencies = \
            xbrl.find_all(name=re.compile("(us-gaap:commitments\
                          andcontingencies)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.commitments_and_contingencies = \
            self.data_processing(commitments_and_contingencies, xbrl,
                ignore_errors, logger, context_ids)

        redeemable_noncontrolling_interest = \
            xbrl.find_all(name=re.compile("(us-gaap:redeemablenoncontrolling\
                          interestequity)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.redeemable_noncontrolling_interest = \
            self.data_processing(redeemable_noncontrolling_interest,
                xbrl, ignore_errors, logger, context_ids)

        temporary_equity = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(temporaryequity)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.temporary_equity = \
            self.data_processing(temporary_equity, xbrl, ignore_errors,
                logger, context_ids)

        equity = xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(equity)",
                               re.IGNORECASE | re.MULTILINE))
        gaap_obj.equity = self.data_processing(equity, xbrl, ignore_errors,
            logger, context_ids)

        equity_attributable_interest = \
            xbrl.find_all(name=re.compile("(us-gaap:minorityinterest)",
                          re.IGNORECASE | re.MULTILINE))
        equity_attributable_interest += \
            xbrl.find_all(name=re.compile("(us-gaap:partnerscapitalattributable\
                          tononcontrollinginterest)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.equity_attributable_interest = \
            self.data_processing(equity_attributable_interest, xbrl,
                ignore_errors, logger, context_ids)

        equity_attributable_parent = \
            xbrl.find_all(name=re.compile("(us-gaap:liabilitiesandpartners\
                          capital)",
                          re.IGNORECASE | re.MULTILINE))
        stockholders_equity = \
            xbrl.find_all(name=re.compile("(us-gaap:stockholdersequity)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.equity_attributable_parent = \
            self.data_processing(equity_attributable_parent, xbrl,
                ignore_errors, logger, context_ids)
        gaap_obj.stockholders_equity = \
            self.data_processing(stockholders_equity, xbrl, ignore_errors,
                logger, context_ids)

        # Incomes #
        revenues = xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(revenue)",
                                 re.IGNORECASE | re.MULTILINE))
        gaap_obj.revenues = self.data_processing(revenues, xbrl,
            ignore_errors, logger, context_ids)

        cost_of_revenue = \
            xbrl.find_all(name=re.compile("(us-gaap:costofrevenue)",
                          re.IGNORECASE | re.MULTILINE))
        cost_of_revenue += \
            xbrl.find_all(name=re.compile("(us-gaap:costffservices)",
                          re.IGNORECASE | re.MULTILINE))
        cost_of_revenue += \
            xbrl.find_all(name=re.compile("(us-gaap:costofgoodssold)",
                          re.IGNORECASE | re.MULTILINE))
        cost_of_revenue += \
            xbrl.find_all(name=re.compile("(us-gaap:costofgoodsand\
                          servicessold)",
                          re.IGNORECASE | re.MULTILINE))

        gross_profit = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(grossprofit)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.gross_profit = \
            self.data_processing(gross_profit, xbrl, ignore_errors,
                                 logger, context_ids)

        operating_expenses = \
            xbrl.find_all(name=re.compile("(us-gaap:operating)[^s]*(expenses)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.operating_expenses = \
            self.data_processing(operating_expenses, xbrl, ignore_errors,
                                 logger, context_ids)

        costs_and_expenses = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(costsandexpenses)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.costs_and_expenses = \
            self.data_processing(costs_and_expenses, xbrl, ignore_errors,
                                 logger, context_ids)

        other_operating_income = \
            xbrl.find_all(name=re.compile("(us-gaap:otheroperatingincome)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.other_operating_income = \
            self.data_processing(other_operating_income, xbrl, ignore_errors,
                                 logger, context_ids)

        operating_income_loss = \
            xbrl.find_all(name=re.compile("(us-gaap:otheroperatingincome)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.operating_income_loss = \
            self.data_processing(operating_income_loss, xbrl, ignore_errors,
                                 logger, context_ids)

        nonoperating_income_loss = \
            xbrl.find_all(name=re.compile("(us-gaap:nonoperatingincomeloss)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.nonoperating_income_loss = \
            self.data_processing(nonoperating_income_loss, xbrl,
                                 ignore_errors, logger, context_ids)

        interest_and_debt_expense = \
            xbrl.find_all(name=re.compile("(us-gaap:interestanddebtexpense)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.interest_and_debt_expense = \
            self.data_processing(interest_and_debt_expense, xbrl,
                                 ignore_errors, logger, context_ids)

        income_before_equity_investments = \
            xbrl.find_all(name=re.compile("(us-gaap:incomelossfromcontinuing"
                                          "operationsbeforeincometaxes"
                                          "minorityinterest)",
                          re.IGNORECASE  | re.MULTILINE))
        gaap_obj.income_before_equity_investments = \
            self.data_processing(income_before_equity_investments, xbrl,
                                 ignore_errors, logger, context_ids)

        income_from_equity_investments = \
            xbrl.find_all(name=re.compile("(us-gaap:incomelossfromequity"
                          "methodinvestments)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_from_equity_investments = \
            self.data_processing(income_from_equity_investments, xbrl,
                                 ignore_errors, logger, context_ids)

        income_tax_expense_benefit = \
            xbrl.find_all(name=re.compile("(us-gaap:incometaxexpensebenefit)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_tax_expense_benefit = \
            self.data_processing(income_tax_expense_benefit, xbrl,
                                 ignore_errors, logger, context_ids)

        income_continuing_operations_tax = \
            xbrl.find_all(name=re.compile("(us-gaap:IncomeLossBeforeExtraordinaryItems\
                          AndCumulativeEffectOfChangeInAccountingPrinciple)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_continuing_operations_tax = \
            self.data_processing(income_continuing_operations_tax, xbrl,
                                 ignore_errors, logger, context_ids)

        income_discontinued_operations = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(discontinued"
                          "operation)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_discontinued_operations = \
            self.data_processing(income_discontinued_operations, xbrl,
                                 ignore_errors, logger, context_ids)

        extraordary_items_gain_loss = \
            xbrl.find_all(name=re.compile("(us-gaap:extraordinaryitem"
                          "netoftax)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.extraordary_items_gain_loss = \
            self.data_processing(extraordary_items_gain_loss, xbrl,
                                 ignore_errors, logger, context_ids)

        income_loss = \
            xbrl.find_all(name=re.compile("(us-gaap:)[^s]*(incomeloss)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_loss = \
            self.data_processing(income_loss, xbrl, ignore_errors,
                logger, context_ids)
        income_loss += xbrl.find_all(name=re.compile("(us-gaap:profitloss)",
                                     re.IGNORECASE | re.MULTILINE))
        gaap_obj.income_loss = \
            self.data_processing(income_loss, xbrl, ignore_errors,
                                 logger, context_ids)

        net_income_shareholders = \
            xbrl.find_all(name=re.compile("(us-gaap:netincomeavailabletocommon\
                          stockholdersbasic)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_income_shareholders = \
            self.data_processing(net_income_shareholders, xbrl, ignore_errors,
                                 logger, context_ids)

        preferred_stock_dividends = \
            xbrl.find_all(name=re.compile("(us-gaap:preferredstockdividendsand\
                          otheradjustments)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.preferred_stock_dividends = \
            self.data_processing(preferred_stock_dividends, xbrl,
                ignore_errors, logger, context_ids)

        net_income_loss_noncontrolling = \
            xbrl.find_all(name=re.compile("(us-gaap:netincomelossattributableto\
                          noncontrollinginterest)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_income_loss_noncontrolling = \
            self.data_processing(net_income_loss_noncontrolling, xbrl,
                                 ignore_errors, logger, context_ids)

        net_income_loss = \
            xbrl.find_all(name=re.compile("^us-gaap:netincomeloss$",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_income_loss = \
            self.data_processing(net_income_loss, xbrl, ignore_errors,
                                 logger, context_ids)

        other_comprehensive_income = \
            xbrl.find_all(name=re.compile("(us-gaap:othercomprehensiveincomeloss\
                          netoftax)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.other_comprehensive_income = \
            self.data_processing(other_comprehensive_income, xbrl,
                ignore_errors, logger, context_ids)

        comprehensive_income = \
            xbrl.find_all(name=re.compile("(us-gaap:comprehensiveincome)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.comprehensive_income = \
            self.data_processing(comprehensive_income, xbrl, ignore_errors,
                                 logger, context_ids)

        comprehensive_income_parent = \
            xbrl.find_all(name=re.compile("(us-gaap:comprehensiveincomenetof"
                          "tax)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.comprehensive_income_parent = \
            self.data_processing(comprehensive_income_parent, xbrl,
                                 ignore_errors, logger, context_ids)

        comprehensive_income_interest = \
            xbrl.find_all(name=re.compile("(us-gaap:comprehensiveincomenetoftax\
                          attributabletononcontrollinginterest)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.comprehensive_income_interest = \
            self.data_processing(comprehensive_income_interest, xbrl,
                                 ignore_errors, logger, context_ids)

        # Cash flow statements #
        net_cash_flows_operating = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          operatingactivities)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_operating = \
            self.data_processing(net_cash_flows_operating, xbrl, ignore_errors,
                                 logger, context_ids)

        net_cash_flows_investing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          investingactivities)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_investing = \
            self.data_processing(net_cash_flows_investing, xbrl, ignore_errors,
                                logger, context_ids)

        net_cash_flows_financing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          financingactivities)", re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_financing = \
            self.data_processing(net_cash_flows_financing, xbrl, ignore_errors,
                                logger, context_ids)

        net_cash_flows_operating_continuing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          operatingactivitiescontinuingoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_operating_continuing = \
            self.data_processing(net_cash_flows_operating_continuing, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_investing_continuing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          investingactivitiescontinuingoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_investing_continuing = \
            self.data_processing(net_cash_flows_investing_continuing, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_financing_continuing = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          financingactivitiescontinuingoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_financing_continuing = \
            self.data_processing(net_cash_flows_financing_continuing, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_operating_discontinued = \
            xbrl.find_all(name=re.compile("(us-gaap:cashprovidedbyusedin\
                          operatingactivitiesdiscontinuedoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_operating_discontinued = \
            self.data_processing(net_cash_flows_operating_discontinued, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_investing_discontinued = \
            xbrl.find_all(name=re.compile("(us-gaap:cashprovidedbyusedin\
                          investingactivitiesdiscontinuedoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_investing_discontinued = \
            self.data_processing(net_cash_flows_investing_discontinued, xbrl,
                                 ignore_errors, logger, context_ids)

        net_cash_flows_discontinued = \
            xbrl.find_all(name=re.compile("(us-gaap:netcashprovidedbyusedin\
                          discontinuedoperations)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.net_cash_flows_discontinued = \
            self.data_processing(net_cash_flows_discontinued, xbrl,
                                 ignore_errors, logger, context_ids)

        common_shares_outstanding = \
            xbrl.find_all(name=re.compile("(us-gaap:commonstockshares\
                          outstanding)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.common_shares_outstanding = \
            self.data_processing(common_shares_outstanding, xbrl,
                                 ignore_errors, logger, context_ids)

        common_shares_issued = \
            xbrl.find_all(name=re.compile("(us-gaap:commonstockshares\
                          issued)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.common_shares_issued = \
            self.data_processing(common_shares_issued, xbrl,
                                 ignore_errors, logger, context_ids)

        common_shares_authorized = \
            xbrl.find_all(name=re.compile("(us-gaap:commonstockshares\
                          authorized)",
                          re.IGNORECASE | re.MULTILINE))
        gaap_obj.common_shares_authorized = \
            self.data_processing(common_shares_authorized, xbrl,
                                 ignore_errors, logger, context_ids)

        return gaap_obj
