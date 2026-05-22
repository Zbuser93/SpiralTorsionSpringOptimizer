from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator
from spiral_torsion_spring_optimizer import SpiralTorsionSpring

app = FastAPI()

class MaximizeStiffnessRequest(BaseModel):
    elasticity: float = Field(gt=0)
    stress_yield: float = Field(gt=0)
    safety_factor: float = Field(gt=0, le=1)
    height: float = Field(gt=0)
    max_radius_pre: float = Field(gt=0)
    radius_center: float = Field(ge=0)
    pitch_0: float = Field(gt=0)
    deltatheta_opt: float = Field(gt=0)
    torque_pre: float = Field(ge=0)
    max_thickness: float | None = Field(default=None, gt=0)
    min_thickness: float | None = Field(default=None, gt=0)
    opt_params: dict | None = Field(default=None)

    @model_validator(mode="after")
    def validate_cross_fields(self) -> "MaximizeStiffnessRequest":
        if self.radius_center >= self.max_radius_pre:
            raise ValueError(
                f"radius_center ({self.radius_center}) must be less than "
                f"max_radius_pre ({self.max_radius_pre})"
            )
        radial_space = self.max_radius_pre - self.radius_center
        if self.pitch_0 >= radial_space:
            raise ValueError(
                f"pitch_0 ({self.pitch_0}) must be less than the available radial space "
                f"max_radius_pre - radius_center = {radial_space:.4g}: "
                "no room for spring coils"
            )
        if self.min_thickness is not None and self.max_thickness is not None:
            if self.min_thickness >= self.max_thickness:
                raise ValueError(
                    f"min_thickness ({self.min_thickness}) must be strictly less than "
                    f"max_thickness ({self.max_thickness})"
                )
        return self

@app.post("/v1/maximize_stiffness")
def maximize_stiffness(req: MaximizeStiffnessRequest):
    try:
        req_data = req.model_dump()
        opt_params = req_data.pop('opt_params', None)
        spring = SpiralTorsionSpring.maximize_stiffness(
            req_data,
            opt_params=opt_params
        )
        return spring.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid inputs: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}