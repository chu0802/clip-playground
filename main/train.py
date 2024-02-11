from copy import deepcopy

from src.datasets.utils import get_dataloaders_from_config
from src.models.clip import get_model
from src.trainer import get_kd_trainer
from src.utils import (
    get_config,
    get_job_id,
    init_distributed_mode,
    is_main_process,
    setup_seeds,
    wandb_logger,
)


@wandb_logger
def main(config):
    job_id = get_job_id() if is_main_process() else None
    setup_seeds(config.task.seed)

    model = get_model(config, device="cuda", freeze=False, pretrained=False)

    dataloaders = get_dataloaders_from_config(config)

    teachers = dict()
    teachers["pretrained"] = get_model(
        config, device="cuda", freeze=True, pretrained=True
    )

    if config.method.name in ["previous_aware_zscl", "mix_teacher", "split_teacher"]:
        # to derive fine-tuned knowledge from teacher, we should not use pre-trained model as the teacher model.
        teachers["prev"] = get_model(
            config, device="cuda", freeze=True, pretrained=False
        )
    elif config.method.name in ["zscl"]:
        teachers["l2"] = get_model(config, device="cuda", freeze=True, pretrained=False)

    trainer = get_kd_trainer(model, dataloaders, config, teachers, job_id)

    # validation provides nearly no information in my experiments
    trainer.train(set_validation=False)

    trainer.logging(
        local_desc="fine-tuned", test_acc=trainer.evaluate(trainer.test_loader)
    )
    trainer.dump_results()


if __name__ == "__main__":
    config = get_config(mode="train")
    init_distributed_mode(config.task)
    main(config)
