from app_gui import AppGUI

if __name__ == '__main__':
    rel1 = "resources"
    rel2 = "outs"
    model_path = "training"
    conf = 0.54

    app = AppGUI(rel1, rel2, model_path, conf)
    app.mainloop()
