from ..app_controller import AppController


'''Rule Interface'''


class Rule:
    def name() -> str:
        pass

    def description() -> str:
        pass

    def match(app_controller: AppController) -> bool:
        pass

    def action(app_controller: AppController) -> None:
        pass


class ViewPagerRule(Rule):
    def name():
        return "Found ViewPager"

    def description():
        return "Swipe left 5 times then back"

    def match(app_controller: AppController):
        return app_controller.highlevel_query.found_view_pager()

    def action(app_controller: AppController):
        for i in range(5):
            app_controller.swipe('left')
            app_controller.delay(1)
        app_controller.back()


rules = [
    ViewPagerRule
]
