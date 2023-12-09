from src.datasets.utils import get_dataloaders, load_class_name_list
from src.models.clip import load_model
from src.template import SIMPLE_TEMPLATE_LIST
from src.trainer import Trainer
from src.utils import get_config, setup_seeds, wandb_logger


@wandb_logger
def main(config):
    setup_seeds(config.task.seed)

    class_name_list = load_class_name_list(config)

    model = load_model(
        config.model,
        class_name_list,
        template_list=SIMPLE_TEMPLATE_LIST,
        device="cuda",
    )

    dataloaders = get_dataloaders(config)

    trainer = Trainer(model, dataloaders, config)

    if trainer.training_mode:
        trainer.train(set_validation=True)

    trainer.logging(test_acc=trainer.evaluate(trainer.test_loader))


if __name__ == "__main__":
    config = get_config()
    main(config)
