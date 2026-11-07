import os
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


@pytest.fixture( scope="function" )
def driver():
    # 提交最终代码脚本时，请将驱动路径换回官方路径"C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe"
    service = Service(
        executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe" )
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get( "https://uutool.cn/tinymce/" )
    driver.maximize_window()
    driver.implicitly_wait( 10 )
    yield driver
    driver.quit()


class TestUutool:

    # test-code-start

    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    import time

    # ---------------- 公共辅助方法（非测试用例，供各测试函数复用） ----------------

    def _frame( self, driver ):
        """切入富文本编辑区 iframe"""
        driver.switch_to.default_content()
        driver.switch_to.frame( driver.find_element( self.By.CSS_SELECTOR, ".tox-edit-area__iframe" ) )

    def _type( self, driver, lines ):
        """在正文区域逐行输入，lines 为字符串列表，行间回车换行"""
        self._frame( driver )
        body = driver.find_element( self.By.ID, "tinymce" )
        body.click()
        for i, text in enumerate( lines ):
            body.send_keys( text )
            if i < len( lines ) - 1:
                body.send_keys( self.Keys.ENTER )
        driver.switch_to.default_content()
        self.time.sleep( 0.3 )

    def _select( self, driver, idx=None ):
        """选中正文：idx=None 时全选（Ctrl+A），否则选中正文第 idx 个子元素"""
        self._frame( driver )
        if idx is None:
            driver.find_element( self.By.ID, "tinymce" ).send_keys( self.Keys.CONTROL, "a" )
        else:
            driver.execute_script(
                "var n=document.body.children[%d];var r=document.createRange();"
                "r.selectNodeContents(n);var s=window.getSelection();"
                "s.removeAllRanges();s.addRange(r);" % idx )
        driver.switch_to.default_content()
        self.time.sleep( 0.3 )

    def _menu( self, driver, name ):
        """点击顶部菜单栏按钮（如 查看/插入/格式/编辑/表格），展开菜单"""
        driver.switch_to.default_content()
        btn = driver.find_element( self.By.XPATH,
            "//button[contains(@class,'tox-mbtn')]//span[text()='%s']/ancestor::button" % name )
        self.ActionChains( driver ).move_to_element( btn ).click().perform()
        self.time.sleep( 0.7 )

    def _item( self, driver, text, click=True ):
        """在已展开的菜单中定位文本为 text 的菜单项；click=True 点击，否则仅悬浮展开子菜单"""
        item = None
        for it in driver.find_elements( self.By.CSS_SELECTOR, ".tox-collection__item" ):
            for lbl in it.find_elements(
                    self.By.CSS_SELECTOR, ".tox-collection__item-label, .tox-collection__item-title" ):
                if lbl.text.strip() == text:
                    item = it
                    break
            if item is not None:
                break
        act = self.ActionChains( driver ).move_to_element( item )
        if click:
            act.click().perform()
        else:
            act.perform()
        self.time.sleep( 0.7 )
        return item

    def _clear( self, driver ):
        """点击底部【清空】按钮，清除正文内容"""
        driver.switch_to.default_content()
        driver.find_element( self.By.CSS_SELECTOR, ".btn-reset" ).click()
        self.time.sleep( 0.8 )

    # ---------------- 测试函数（每个需求对应一个函数） ----------------

    def test_Uutool_R001( self, driver ):
        """需求1：两行内容分别设为一级标题、二级标题，预览后截图（4条用例）"""
        self.time.sleep( 2 )
        cases = [("Web应用测试", "个人赛"), ("Web应用测试", "团队赛"),
                 ("开发者测试", "个人赛"), ("开发者测试", "团队赛")]
        for i, (line1, line2) in enumerate( cases ):
            if i:
                self._clear( driver )
            self._type( driver, [line1, line2] )
            self._select( driver, 0 )
            driver.find_element( self.By.XPATH, "//button[@aria-label='样式']" ).click()
            self.time.sleep( 0.6 )
            self._item( driver, "一级标题" )
            self._select( driver, 1 )
            driver.find_element( self.By.XPATH, "//button[@aria-label='样式']" ).click()
            self.time.sleep( 0.6 )
            self._item( driver, "二级标题" )
            self._menu( driver, "查看" )
            self._item( driver, "预览" )
            self.time.sleep( 0.5 )
            self.take_screenshot( driver, "Uutool_R001_00%d.png" % (i + 1) )
            driver.find_element( self.By.XPATH,
                "//div[contains(@class,'tox-dialog__footer')]//button[normalize-space()='关闭']" ).click()
            self.time.sleep( 0.5 )

    def test_Uutool_R002( self, driver ):
        """需求2：正文叠加加粗、斜体、下划线、删除线四种格式（2条用例）"""
        self.time.sleep( 2 )
        for i, text in enumerate( ["全国大学生软件测试大赛", "慕测平台"] ):
            if i:
                self._clear( driver )
            self._type( driver, [text] )
            self._select( driver )
            for label in ["粗体", "斜体", "下划线", "删除线"]:
                driver.find_element( self.By.XPATH, "//button[@aria-label='%s']" % label ).click()
                self.time.sleep( 0.3 )
            self.take_screenshot( driver, "Uutool_R002_00%d.png" % (i + 1) )

    def test_Uutool_R003( self, driver ):
        """需求3：第一行设为有序列表、第二行设为无序列表（2条用例）"""
        self.time.sleep( 2 )
        for i, line2 in enumerate( ["Java代码", "Python代码"] ):
            if i:
                self._clear( driver )
            self._type( driver, ["Web应用测试", line2] )
            self._select( driver, 0 )
            driver.find_element( self.By.XPATH, "//div[@aria-label='有序列表']" ).click()
            self.time.sleep( 0.4 )
            self._select( driver, 1 )
            driver.find_element( self.By.XPATH, "//div[@aria-label='无序列表']" ).click()
            self.time.sleep( 0.4 )
            self.take_screenshot( driver, "Uutool_R003_00%d.png" % (i + 1) )

    def test_Uutool_R004( self, driver ):
        """需求4：正文设置为 Arial Black 字体、18pt 字号（1条用例）"""
        self.time.sleep( 2 )
        self._type( driver, ["全国大学生软件测试大赛"] )
        self._select( driver )
        driver.find_element( self.By.XPATH, "//button[@aria-label='字体']" ).click()
        self.time.sleep( 0.6 )
        self._item( driver, "Arial Black" )
        driver.find_element( self.By.XPATH, "//button[@aria-label='字体大小']" ).click()
        self.time.sleep( 0.6 )
        self._item( driver, "18pt" )
        self.take_screenshot( driver, "Uutool_R004_001.png" )

    def test_Uutool_R005( self, driver ):
        """需求5：为“慕测平台”添加链接后截图（1条用例）"""
        self.time.sleep( 2 )
        self._type( driver, ["慕测平台"] )
        self._select( driver )
        self._menu( driver, "插入" )
        self._item( driver, "链接..." )
        driver.find_elements( self.By.CSS_SELECTOR, ".tox-dialog input" )[0].send_keys(
            "http://www.mooctest.net/#/login" )
        driver.find_element( self.By.XPATH,
            "//div[contains(@class,'tox-dialog__footer')]//button[normalize-space()='保存']" ).click()
        self.time.sleep( 0.8 )
        self.take_screenshot( driver, "Uutool_R005_001.png" )

    def test_Uutool_R006( self, driver ):
        """需求6：插入3行4列表格，合并首行，逐格填充，全表居中（1条用例）"""
        self.time.sleep( 2 )
        self._menu( driver, "表格" )
        self._item( driver, "表格", click=False )
        cells = driver.find_elements( self.By.CSS_SELECTOR, ".tox-insert-table-picker div" )
        self.ActionChains( driver ).move_to_element( cells[(3 - 1) * 10 + (4 - 1)] ).click().perform()
        self.time.sleep( 0.8 )
        self._frame( driver )
        tds = driver.find_elements( self.By.CSS_SELECTOR, "td" )
        self.ActionChains( driver ).click_and_hold( tds[0] ).move_to_element( tds[3] ).release().perform()
        self.time.sleep( 0.4 )
        self.ActionChains( driver ).context_click( tds[1] ).perform()
        driver.switch_to.default_content()
        self.time.sleep( 0.8 )
        self._item( driver, "单元格", click=False )
        self._item( driver, "合并单元格" )
        self._frame( driver )
        body = driver.find_element( self.By.ID, "tinymce" )
        body.send_keys( "Selenium操作" )
        for cell in ["浏览器Cookie管理", "点击鼠标右键", "鼠标移动到某个坐标", "全选",
                     "driver.manage().addCookie()", "contextClick()", "moveByOffset()",
                     '(Keys.CONTROL,"a")']:
            body.send_keys( self.Keys.TAB )
            self.time.sleep( 0.2 )
            body.send_keys( cell )
        self.time.sleep( 0.4 )
        tds = driver.find_elements( self.By.CSS_SELECTOR, "td" )
        self.ActionChains( driver ).move_to_element_with_offset(
            tds[0], -10, -5 ).click_and_hold().move_to_element( tds[-1] ).release().perform()
        self.time.sleep( 0.4 )
        driver.switch_to.default_content()
        driver.find_element( self.By.XPATH, "//button[@aria-label='居中对齐']" ).click()
        self.time.sleep( 0.5 )
        self.take_screenshot( driver, "Uutool_R006_001.png" )

    def test_Uutool_R007( self, driver ):
        """需求7：插入图片并设置尺寸、间距与实线边框（1条用例）"""
        self.time.sleep( 2 )
        driver.find_element( self.By.XPATH, "//button[@aria-label='更多...']" ).click()
        self.time.sleep( 0.8 )
        driver.find_element( self.By.XPATH, "//button[@aria-label='插入/编辑图片']" ).click()
        self.time.sleep( 0.8 )
        def inp( label ):
            return driver.find_element( self.By.XPATH,
                "//label[text()='%s']/following::input[1]" % label )
        inp( "源" ).send_keys( "https://www.mooctest.net/img/logo.a000b55f.jpg" )
        inp( "替代描述" ).send_keys( "慕测平台Logo" )
        driver.find_element( self.By.XPATH, "//button[@title='保持比例']" ).click()
        self.time.sleep( 0.3 )
        width = inp( "宽度" )
        width.clear()
        width.send_keys( "200" )
        height = inp( "高度" )
        height.clear()
        height.send_keys( "200" )
        for tab in driver.find_elements( self.By.CSS_SELECTOR, ".tox-tab" ):
            if tab.text == "高级":
                tab.click()
        self.time.sleep( 0.6 )
        inp( "垂直间距" ).send_keys( "10" )
        inp( "水平间距" ).send_keys( "10" )
        inp( "边框宽度" ).send_keys( "2" )
        driver.find_element( self.By.XPATH, "//button[@title='边框样式']" ).click()
        self.time.sleep( 0.8 )
        self._item( driver, "实线" )
        driver.find_element( self.By.XPATH,
            "//div[contains(@class,'tox-dialog__footer')]//button[normalize-space()='保存']" ).click()
        self.time.sleep( 3.5 )
        self.take_screenshot( driver, "Uutool_R007_001.png" )

    def test_Uutool_R008( self, driver ):
        """需求8：正文设为代码格式后查看源代码并截图（1条用例）"""
        self.time.sleep( 2 )
        self._type( driver, ["Web应用测试"] )
        self._select( driver )
        self._menu( driver, "格式" )
        self._item( driver, "代码" )
        self._menu( driver, "查看" )
        self._item( driver, "源代码" )
        self.time.sleep( 0.6 )
        self.take_screenshot( driver, "Uutool_R008_001.png" )

    def test_Uutool_R009( self, driver ):
        """需求9：点击【复制HTML】与【下载HTML】后截图（1条用例）"""
        self.time.sleep( 2 )
        self._type( driver, ["全国大学生软件测试大赛"] )
        driver.switch_to.default_content()
        driver.find_element( self.By.CSS_SELECTOR, ".btn-copy" ).click()
        self.time.sleep( 0.5 )
        driver.find_element( self.By.CSS_SELECTOR, ".btn-export" ).click()
        self.time.sleep( 0.5 )
        self.take_screenshot( driver, "Uutool_R009_001.png" )

    def test_Uutool_R010( self, driver ):
        """需求10：查找“测试”并全部替换为“比赛”后截图（1条用例）"""
        self.time.sleep( 2 )
        self._type( driver, ["全国大学生软件测试大赛Web应用测试"] )
        self._menu( driver, "编辑" )
        self._item( driver, "查找并替换..." )
        fields = driver.find_elements( self.By.CSS_SELECTOR, ".tox-textfield" )
        fields[0].send_keys( "测试" )
        fields[1].send_keys( "比赛" )
        driver.find_element( self.By.XPATH,
            "//div[contains(@class,'tox-dialog__footer')]//button[normalize-space()='寻找']" ).click()
        self.time.sleep( 0.5 )
        driver.find_element( self.By.XPATH,
            "//div[contains(@class,'tox-dialog__footer')]//button[normalize-space()='替换全部']" ).click()
        self.time.sleep( 0.5 )
        driver.find_element( self.By.XPATH, "//button[@aria-label='关闭']" ).click()
        self.time.sleep( 0.5 )
        self.take_screenshot( driver, "Uutool_R010_001.png" )

    def test_Uutool_R011( self, driver ):
        """需求11：正文设置为红色文字后截图（1条用例）"""
        self.time.sleep( 2 )
        self._type( driver, ["全国大学生软件测试大赛"] )
        self._select( driver )
        self._menu( driver, "格式" )
        self._item( driver, "文本颜色", click=False )
        red = driver.find_element( self.By.CSS_SELECTOR, ".tox-swatch[title='红色']" )
        self.ActionChains( driver ).move_to_element( red ).click().perform()
        self.time.sleep( 0.5 )
        self.take_screenshot( driver, "Uutool_R011_001.png" )

    # test-code-end

    @staticmethod
    def take_screenshot(driver, file_name):
        timestamp = datetime.now().strftime( "%H%M%S%d%f" )[:-3]
        timestamped_file_name = f"{timestamp}_{file_name}"
        screenshots_dir = "screenshots"
        if not os.path.exists( screenshots_dir ):
            os.makedirs( screenshots_dir )
        screenshot_file_path = os.path.join( screenshots_dir, timestamped_file_name )
        driver.save_screenshot( screenshot_file_path )
