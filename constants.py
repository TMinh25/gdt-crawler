class Constant(object):
    SELECTOR = {
        "modalContentTag": "div.ant-modal-content",
        "closeModalContentX": '//button[@aria-label="Close" and contains(@class, "ant-modal-close")]',
        "openLoginFormX": '//span[text()="Đăng nhập"]',
        "usernameInput": "input#username",
        "passwordInput": "input#password",
        "captchaImgTag": "body > div:nth-child(9) > div > div.ant-modal-wrap.ant-modal-centered > div > div.ant-modal-content > div.ant-modal-body > form > div > div:nth-child(3) > div > div.ant-col.ant-col-24.ant-form-item-control-wrapper > div > span > div > img",
        "captchaInputTag": "div.ant-modal-content input#cvalue",
        "loginButtonTag": "//button[@type='submit' and span[text()='Đăng nhập']]",
        "next_data": "script#__NEXT_DATA__",
    }
