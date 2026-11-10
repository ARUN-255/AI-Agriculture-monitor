from pathlib import Path
from PIL import Image
import io
class DiseaseClassifier:
 def __init__(self,model_path,labels_path):
  self.model_path=Path(model_path); self.labels_path=Path(labels_path); self.interpreter=None; self.labels=[]
  if self.model_path.exists() and self.labels_path.exists():
   try:
    import tensorflow as tf
    self.interpreter=tf.lite.Interpreter(model_path=str(self.model_path)); self.interpreter.allocate_tensors(); self.input=self.interpreter.get_input_details()[0]; self.output=self.interpreter.get_output_details()[0]; self.labels=[x.strip() for x in self.labels_path.read_text().splitlines() if x.strip()]
   except Exception:self.interpreter=None
 @property
 def ready(self):return self.interpreter is not None and bool(self.labels)
 def predict(self,raw):
  if not self.ready:return {"status":"model_not_configured","message":"Add a compatible PlantVillage-trained TensorFlow Lite model and labels file to backend/models to enable predictions."}
  import numpy as np
  image=Image.open(io.BytesIO(raw)).convert("RGB").resize((self.input["shape"][2],self.input["shape"][1])); tensor=np.asarray(image,dtype=np.float32)[None,...]; scale,zero=self.input.get("quantization",(0.0,0))
  tensor=(tensor/scale+zero).astype(self.input["dtype"]) if scale else (tensor/255.0).astype(self.input["dtype"])
  self.interpreter.set_tensor(self.input["index"],tensor); self.interpreter.invoke(); scores=self.interpreter.get_tensor(self.output["index"])[0]; idx=int(np.argmax(scores)); label=self.labels[idx] if idx<len(self.labels) else f"class_{idx}"
  return {"status":"ok","disease":label,"confidence":round(float(scores[idx]),4),"treatment":treatment_for(label)}
def treatment_for(label):
 key=label.lower()
 if "healthy" in key:return "The model classified this leaf as healthy. Continue routine monitoring and avoid unnecessary spraying."
 if "blight" in key:return "Remove badly affected leaves, avoid overhead watering, improve air circulation and consult local agricultural extension guidance before applying a registered treatment."
 if "rust" in key:return "Remove heavily affected plant debris, keep foliage dry where practical and seek local agronomy advice on an approved treatment."
 return "Isolate visibly affected plants where practical, remove severely diseased debris safely and confirm the result with a local agricultural expert before treatment."
