package dev.shutrwise.probe;

// THROWAWAY Camera2 evidence probe. No product architecture or image enhancement.
import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.ImageFormat;
import android.graphics.Rect;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.*;
import android.hardware.camera2.params.*;
import android.media.Image;
import android.media.ImageReader;
import android.os.*;
import android.util.*;
import android.view.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.lang.reflect.Array;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivity extends Activity {
    CameraManager manager;
    HandlerThread thread;
    Handler worker;
    Handler ui = new Handler(Looper.getMainLooper());
    TextView stateView;
    TextureView preview;
    CameraDevice camera;
    CameraCaptureSession session;
    ImageReader reader;
    Surface previewSurface;
    CameraCharacteristics characteristics;
    TotalCaptureResult baseline;
    JSONObject report;
    File runDir;
    String cameraId, mode;
    boolean submitted, finished;
    int expected, written;
    long warmupStart;
    Map<Long, Image> images = new HashMap<>();
    Map<Long, TotalCaptureResult> results = new HashMap<>();
    Map<Integer, Long> started = new HashMap<>();
    List<JSONObject> plans = new ArrayList<>();

    static void put(JSONObject obj, String key, Object value) {
        try { obj.put(key, value == null ? JSONObject.NULL : value); }
        catch (JSONException e) { throw new IllegalArgumentException(e); }
    }
    static Object json(Object value) {
        if (value == null) return JSONObject.NULL;
        if (value instanceof Rational) {
            Rational r=(Rational)value; JSONObject rational=new JSONObject();
            put(rational,"numerator",r.getNumerator()); put(rational,"denominator",r.getDenominator()); return rational;
        }
        if (value instanceof Number) {
            double d = ((Number)value).doubleValue();
            return Double.isFinite(d) ? value : value.toString();
        }
        if (value instanceof String || value instanceof Boolean) return value;
        JSONObject obj = new JSONObject();
        if (value instanceof Size) {
            put(obj,"width",((Size)value).getWidth()); put(obj,"height",((Size)value).getHeight()); return obj;
        }
        if (value instanceof SizeF) {
            put(obj,"width",((SizeF)value).getWidth()); put(obj,"height",((SizeF)value).getHeight()); return obj;
        }
        if (value instanceof Range) {
            put(obj,"lower",json(((Range<?>)value).getLower())); put(obj,"upper",json(((Range<?>)value).getUpper())); return obj;
        }
        if (value instanceof Rect) {
            Rect r=(Rect)value;
            put(obj,"left",r.left); put(obj,"top",r.top); put(obj,"right",r.right); put(obj,"bottom",r.bottom); return obj;
        }
        if (value instanceof RggbChannelVector) {
            RggbChannelVector v=(RggbChannelVector)value;
            put(obj,"red",v.getRed()); put(obj,"green_even",v.getGreenEven()); put(obj,"green_odd",v.getGreenOdd()); put(obj,"blue",v.getBlue()); return obj;
        }
        if (value.getClass().isArray()) {
            JSONArray arr=new JSONArray();
            for (int i=0;i<Array.getLength(value);i++) arr.put(json(Array.get(value,i)));
            return arr;
        }
        if (value instanceof Collection) {
            JSONArray arr=new JSONArray(); for (Object x:(Collection<?>)value) arr.put(json(x)); return arr;
        }
        put(obj,"java_type",value.getClass().getName()); put(obj,"string_value",value.toString()); return obj;
    }
    static String stamp() {
        SimpleDateFormat f=new SimpleDateFormat("yyyyMMdd'T'HHmmssSSS'Z'",Locale.US);
        f.setTimeZone(TimeZone.getTimeZone("UTC")); return f.format(new Date());
    }
    static boolean has(int[] values,int wanted) {
        if(values!=null)for(int v:values)if(v==wanted)return true; return false;
    }
    void file(File path,JSONObject object) throws Exception {
        try(FileOutputStream out=new FileOutputStream(path)) { out.write(object.toString(2).getBytes("UTF-8")); }
    }
    void log(String state) {
        if(report!=null) {
            put(report,"state",state);
            put(report,"updated_at_utc",stamp());
            try { file(new File(runDir,"run.json"),report); } catch(Exception e) { Log.e("ShutrwiseProbe","Report write",e); }
            String text=report.toString(); ui.post(()->stateView.setText(text));
        }
        Log.i("ShutrwiseProbe",state);
    }
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        LinearLayout layout=new LinearLayout(this); layout.setOrientation(LinearLayout.VERTICAL);
        TextView heading=new TextView(this); heading.setText("Shutrwise Camera2 Probe · THROWAWAY");
        layout.addView(heading);
        preview=new TextureView(this); layout.addView(preview,new LinearLayout.LayoutParams(-1,400));
        LinearLayout buttons=new LinearLayout(this);
        Button dump=new Button(this); dump.setText("Capabilities"); dump.setOnClickListener(v->worker.post(()->dumpCapabilities())); buttons.addView(dump);
        Button shot=new Button(this); shot.setText("Single RAW"); shot.setOnClickListener(v->startCapture("0","single")); buttons.addView(shot);
        Button bracket=new Button(this); bracket.setText("RAW bracket"); bracket.setOnClickListener(v->startCapture("0","bracket")); buttons.addView(bracket);
        layout.addView(buttons);
        ScrollView scroll=new ScrollView(this); stateView=new TextView(this); stateView.setText("Waiting for command"); scroll.addView(stateView); layout.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        setContentView(layout);
        manager=(CameraManager)getSystemService(CAMERA_SERVICE);
        thread=new HandlerThread("probe-camera"); thread.start(); worker=new Handler(thread.getLooper());
        if(checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED) requestPermissions(new String[]{Manifest.permission.CAMERA},1);
        else command(getIntent());
    }
    @Override public void onNewIntent(Intent intent) { super.onNewIntent(intent); setIntent(intent); command(intent); }
    @Override public void onRequestPermissionsResult(int code,String[] permissions,int[] results) {
        super.onRequestPermissionsResult(code,permissions,results);
        if(results.length>0&&results[0]==PackageManager.PERMISSION_GRANTED)command(getIntent());
        else stateView.setText("Camera permission denied; no capture performed.");
    }
    void command(Intent intent) {
        String action=intent.getStringExtra("action");
        if("capture".equals(action))startCapture(intent.getStringExtra("camera_id"),intent.getStringExtra("mode"));
        else worker.post(()->dumpCapabilities());
    }
    JSONObject metadata(CameraCharacteristics c) {
        JSONObject values=new JSONObject();
        for(CameraCharacteristics.Key<?> key:c.getKeys()) {
            try { put(values,key.getName(),json(c.get(key))); }
            catch(Exception e) { put(values,key.getName()+".read_error",e.toString()); }
        }
        return values;
    }
    JSONObject streamMap(StreamConfigurationMap map) {
        JSONObject result=new JSONObject(); if(map==null)return result;
        for(int format:map.getOutputFormats()) {
            JSONObject f=new JSONObject();
            put(f,"format",format);
            put(f,"name",format==ImageFormat.RAW_SENSOR?"RAW_SENSOR":format==ImageFormat.JPEG?"JPEG":format==ImageFormat.YUV_420_888?"YUV_420_888":format==ImageFormat.RAW10?"RAW10":format==ImageFormat.RAW12?"RAW12":"OTHER");
            JSONArray sizes=new JSONArray();
            Size[] regular=map.getOutputSizes(format);
            if(regular!=null)for(Size s:regular) {
                JSONObject item=(JSONObject)json(s);
                put(item,"minimum_frame_duration_ns",map.getOutputMinFrameDuration(format,s));
                put(item,"stall_duration_ns",map.getOutputStallDuration(format,s)); sizes.put(item);
            }
            put(f,"sizes",sizes); put(f,"high_resolution_sizes",json(map.getHighResolutionOutputSizes(format)));
            put(result,String.valueOf(format),f);
        }
        put(result,"surface_texture_sizes",json(map.getOutputSizes(SurfaceTexture.class))); return result;
    }
    JSONArray requestKeys(List<CaptureRequest.Key<?>> keys) {
        JSONArray arr=new JSONArray(); if(keys!=null)for(CaptureRequest.Key<?> key:keys)arr.put(key.getName()); return arr;
    }
    JSONObject cameraRecord(String id,boolean listed) throws Exception {
        CameraCharacteristics c=manager.getCameraCharacteristics(id);
        JSONObject item=new JSONObject(); put(item,"id",id); put(item,"listed_by_camera_manager",listed);
        put(item,"characteristics",metadata(c)); put(item,"physical_camera_ids",json(c.getPhysicalCameraIds()));
        put(item,"streams",streamMap(c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)));
        put(item,"maximum_resolution_streams",streamMap(c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP_MAXIMUM_RESOLUTION)));
        put(item,"request_keys",requestKeys(c.getAvailableCaptureRequestKeys()));
        JSONArray results=new JSONArray(); for(CaptureResult.Key<?> key:c.getAvailableCaptureResultKeys())results.put(key.getName()); put(item,"result_keys",results);
        put(item,"session_keys",requestKeys(c.getAvailableSessionKeys()));put(item,"physical_request_keys",requestKeys(c.getAvailablePhysicalCameraRequestKeys()));
        return item;
    }
    void dumpCapabilities() {
        try {
            JSONObject out=new JSONObject(); put(out,"recorded_at_utc",stamp()); put(out,"manufacturer",Build.MANUFACTURER);put(out,"model",Build.MODEL);put(out,"android_version",Build.VERSION.RELEASE);put(out,"api_level",Build.VERSION.SDK_INT);
            put(out,"source","CameraManager and CameraCharacteristics, dev.shutrwise.probe");
            JSONArray listed=new JSONArray();JSONArray physical=new JSONArray();Set<String> physicalIds=new TreeSet<>();
            String[] ids=manager.getCameraIdList();put(out,"camera_ids",json(ids));
            for(String id:ids) {
                try { listed.put(cameraRecord(id,true));physicalIds.addAll(manager.getCameraCharacteristics(id).getPhysicalCameraIds()); }
                catch(Exception e) { JSONObject fail=new JSONObject();put(fail,"id",id);put(fail,"error",e.toString());listed.put(fail); }
            }
            for(String id:physicalIds)if(!Arrays.asList(ids).contains(id)) {
                try { physical.put(cameraRecord(id,false)); }
                catch(Exception e) { JSONObject fail=new JSONObject();put(fail,"id",id);put(fail,"error",e.toString());physical.put(fail); }
            }
            put(out,"listed_cameras",listed);put(out,"additional_physical_camera_characteristics",physical);
            file(new File(getFilesDir(),"capabilities.json"),out);
            ui.post(()->stateView.setText(out.toString()));Log.i("ShutrwiseProbe","CAPABILITIES_SAVED");
        }catch(Exception e){ui.post(()->stateView.setText(e.toString()));Log.e("ShutrwiseProbe","Capability dump",e);}
    }
    void startCapture(String id,String requestedMode) {
        final String chosenId=id==null?"0":id;
        final String chosenMode="control".equals(requestedMode)?"control":("bracket".equals(requestedMode)?"bracket":"single");
        if(!chosenId.matches("[a-zA-Z0-9_.-]+")){stateView.setText("Invalid camera ID");return;}
        Runnable begin=()->worker.post(()->open(chosenId,chosenMode));
        if(preview.isAvailable())begin.run();
        else preview.setSurfaceTextureListener(new TextureView.SurfaceTextureListener(){
            public void onSurfaceTextureAvailable(SurfaceTexture t,int w,int h){begin.run();}
            public void onSurfaceTextureSizeChanged(SurfaceTexture t,int w,int h){}
            public boolean onSurfaceTextureDestroyed(SurfaceTexture t){return true;}
            public void onSurfaceTextureUpdated(SurfaceTexture t){}
        });
    }
    void open(String id,String selectedMode) {
        if(camera!=null){Log.w("ShutrwiseProbe","Capture already active");return;}
        cameraId=id;mode=selectedMode;finished=false;submitted=false;baseline=null;written=0;expected=mode.equals("control")?4:(mode.equals("bracket")?3:1);plans.clear();started.clear();images.clear();results.clear();
        runDir=new File(getFilesDir(),"runs/"+stamp()+"-camera"+id+"-"+mode);runDir.mkdirs();report=new JSONObject();
        put(report,"camera_id",id);put(report,"mode",mode);put(report,"model",Build.MODEL);put(report,"expected_frames",expected);put(report,"created_at_utc",stamp());put(report,"dngs_written",0);put(report,"matching","RAW image timestamp equals result SENSOR_TIMESTAMP");log("OPENING");
        try {
            characteristics=manager.getCameraCharacteristics(id);
            int[] caps=characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES);
            if(!has(caps,CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_RAW)||!has(caps,CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_MANUAL_SENSOR))throw new IllegalStateException("Camera does not advertise both RAW and MANUAL_SENSOR");
            StreamConfigurationMap map=characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);
            Size[] rawSizes=map.getOutputSizes(ImageFormat.RAW_SENSOR);
            if(rawSizes==null||rawSizes.length==0)throw new IllegalStateException("No RAW_SENSOR output sizes");
            Size raw=Collections.max(Arrays.asList(rawSizes),Comparator.comparingLong(s->(long)s.getWidth()*s.getHeight()));
            Size[] previewSizes=map.getOutputSizes(SurfaceTexture.class);Size previewSize=previewSizes[0];
            for(Size s:previewSizes)if(s.getWidth()==640&&s.getHeight()==480)previewSize=s;
            SurfaceTexture texture=preview.getSurfaceTexture();texture.setDefaultBufferSize(previewSize.getWidth(),previewSize.getHeight());previewSurface=new Surface(texture);
            reader=ImageReader.newInstance(raw.getWidth(),raw.getHeight(),ImageFormat.RAW_SENSOR,6);
            reader.setOnImageAvailableListener(r->{
                try {
                    Image image;
                    while((image=r.acquireNextImage())!=null) {
                        if(finished){image.close();continue;}
                        long ts=image.getTimestamp();images.put(ts,image);pair(ts);
                    }
                }catch(Exception e){fail(e);}
            },worker);
            put(report,"raw_size",json(raw));put(report,"preview_size",json(previewSize));put(report,"raw_minimum_frame_duration_ns",map.getOutputMinFrameDuration(ImageFormat.RAW_SENSOR,raw));put(report,"raw_stall_duration_ns",map.getOutputStallDuration(ImageFormat.RAW_SENSOR,raw));put(report,"timestamp_source",characteristics.get(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE));
            file(new File(runDir,"characteristics.json"),cameraRecord(id,true));
            worker.postDelayed(()->{if(!finished)fail(new IllegalStateException("Capture timed out after 90 seconds"));},90000);
            manager.openCamera(id,new CameraDevice.StateCallback(){
                public void onOpened(CameraDevice d){camera=d;configure();}
                public void onDisconnected(CameraDevice d){d.close();fail(new IllegalStateException("Camera disconnected"));}
                public void onError(CameraDevice d,int error){d.close();fail(new IllegalStateException("Camera error "+error));}
            },worker);
        }catch(Exception e){fail(e);}
    }
    void configure() {
        try {
            camera.createCaptureSession(Arrays.asList(previewSurface,reader.getSurface()),new CameraCaptureSession.StateCallback(){
                public void onConfigured(CameraCaptureSession s){session=s;warmup();}
                public void onConfigureFailed(CameraCaptureSession s){fail(new IllegalStateException("RAW + preview session configuration failed"));}
            },worker);
        }catch(Exception e){fail(e);}
    }
    void warmup() {
        try {
            CaptureRequest.Builder b=camera.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);b.addTarget(previewSurface);
            b.set(CaptureRequest.CONTROL_AE_MODE,CaptureRequest.CONTROL_AE_MODE_ON);
            int[] modes=characteristics.get(CameraCharacteristics.CONTROL_AF_AVAILABLE_MODES);
            if(has(modes,CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE))b.set(CaptureRequest.CONTROL_AF_MODE,CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE);
            warmupStart=SystemClock.elapsedRealtime();log("METERING_PREVIEW");
            session.setRepeatingRequest(b.build(),new CameraCaptureSession.CaptureCallback(){
                public void onCaptureCompleted(CameraCaptureSession s,CaptureRequest r,TotalCaptureResult result){
                    if(submitted||finished)return;baseline=result;
                    long elapsed=SystemClock.elapsedRealtime()-warmupStart;
                    Integer ae=result.get(CaptureResult.CONTROL_AE_STATE);
                    if(elapsed>=2500&&(Integer.valueOf(CaptureResult.CONTROL_AE_STATE_CONVERGED).equals(ae)||elapsed>=5000))submit();
                }
            },worker);
        }catch(Exception e){fail(e);}
    }
    JSONObject resultJson(TotalCaptureResult result) {
        JSONObject values=new JSONObject();for(CaptureResult.Key<?> key:result.getKeys()) {
            try { put(values,key.getName(),json(result.get(key))); }
            catch(Exception e){put(values,key.getName()+".read_error",e.toString());}
        }return values;
    }
    void submit() {
        submitted=true;
        try {
            Long baseTime=baseline.get(CaptureResult.SENSOR_EXPOSURE_TIME);Integer baseIso=baseline.get(CaptureResult.SENSOR_SENSITIVITY);
            if(baseTime==null||baseIso==null)throw new IllegalStateException("Preview returned no exposure/ISO baseline");
            Range<Long> timeRange=characteristics.get(CameraCharacteristics.SENSOR_INFO_EXPOSURE_TIME_RANGE);
            Range<Integer> isoRange=characteristics.get(CameraCharacteristics.SENSOR_INFO_SENSITIVITY_RANGE);
            int iso=isoRange.clamp(baseIso);Float focus=baseline.get(CaptureResult.LENS_FOCUS_DISTANCE);
            file(new File(runDir,"baseline-result.json"),resultJson(baseline));put(report,"baseline_exposure_time_ns",baseTime);put(report,"baseline_iso",baseIso);put(report,"baseline_focus_distance",focus);put(report,"baseline_ae_state",baseline.get(CaptureResult.CONTROL_AE_STATE));put(report,"baseline_af_state",baseline.get(CaptureResult.CONTROL_AF_STATE));
            JSONArray planned=new JSONArray();List<CaptureRequest> requests=new ArrayList<>();
            int[] offsets=mode.equals("control")?new int[]{-2,0,2,2}:(mode.equals("bracket")?new int[]{-2,0,2}:new int[]{0});
            for(int i=0;i<offsets.length;i++) {
                long desired=Math.round(baseTime*Math.pow(2,offsets[i]));long exposure=timeRange.clamp(desired);
                boolean longSingle=mode.equals("control")&&i==3;
                int unclampedIso=longSingle?(int)Math.round((double)iso*baseTime/exposure):iso;
                int frameIso=isoRange.clamp(unclampedIso);
                CaptureRequest.Builder b=camera.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE);b.addTarget(reader.getSurface());b.addTarget(previewSurface);b.setTag(i);
                b.set(CaptureRequest.CONTROL_AE_MODE,CaptureRequest.CONTROL_AE_MODE_OFF);b.set(CaptureRequest.SENSOR_EXPOSURE_TIME,exposure);b.set(CaptureRequest.SENSOR_SENSITIVITY,frameIso);
                Long maxFrame=characteristics.get(CameraCharacteristics.SENSOR_INFO_MAX_FRAME_DURATION);
                long minFrame=report.optLong("raw_minimum_frame_duration_ns");long frame=Math.max(exposure,minFrame);
                if(maxFrame!=null)frame=Math.min(frame,maxFrame);b.set(CaptureRequest.SENSOR_FRAME_DURATION,frame);
                boolean focusManual=focus!=null&&has(characteristics.get(CameraCharacteristics.CONTROL_AF_AVAILABLE_MODES),CaptureRequest.CONTROL_AF_MODE_OFF);
                if(focusManual){b.set(CaptureRequest.CONTROL_AF_MODE,CaptureRequest.CONTROL_AF_MODE_OFF);b.set(CaptureRequest.LENS_FOCUS_DISTANCE,focus);}
                boolean wbLock=Boolean.TRUE.equals(characteristics.get(CameraCharacteristics.CONTROL_AWB_LOCK_AVAILABLE));if(wbLock)b.set(CaptureRequest.CONTROL_AWB_LOCK,true);
                JSONObject plan=new JSONObject();put(plan,"index",i);put(plan,"offset_ev",longSingle?0:offsets[i]);put(plan,"frame_role",longSingle?"longer_lower_iso_single":(i==1?"metered_middle_raw":"fixed_iso_exposure"));put(plan,"requested_exposure_time_ns",exposure);put(plan,"unclamped_exposure_time_ns",desired);put(plan,"requested_iso",frameIso);put(plan,"unclamped_iso",unclampedIso);put(plan,"iso_clamped",frameIso!=unclampedIso);put(plan,"requested_shutter_iso_product",(double)exposure*frameIso);put(plan,"baseline_shutter_iso_product",(double)baseTime*iso);put(plan,"requested_product_ratio_to_baseline",((double)exposure*frameIso)/((double)baseTime*iso));put(plan,"nominal_product_model","Shutter times ISO is a nominal exposure model, not calibrated analogue gain");put(plan,"requested_frame_duration_ns",frame);put(plan,"manual_focus_requested",focusManual);put(plan,"requested_focus_distance",focusManual?focus:null);put(plan,"awb_lock_requested",wbLock);put(plan,"exposure_clamped",desired!=exposure);
                plans.add(plan);planned.put(plan);requests.add(b.build());
            }
            put(report,"plan",planned);put(report,"submission_method",expected>1?"captureBurst":"capture");log("CAPTURING");session.stopRepeating();put(report,"submitted_elapsed_realtime_ns",SystemClock.elapsedRealtimeNanos());
            CameraCaptureSession.CaptureCallback callback=new CameraCaptureSession.CaptureCallback(){
                public void onCaptureStarted(CameraCaptureSession s,CaptureRequest r,long timestamp,long frameNumber){started.put((Integer)r.getTag(),timestamp);}
                public void onCaptureCompleted(CameraCaptureSession s,CaptureRequest r,TotalCaptureResult result){
                    try {Long ts=result.get(CaptureResult.SENSOR_TIMESTAMP);if(ts==null)throw new IllegalStateException("No sensor timestamp");results.put(ts,result);pair(ts);}
                    catch(Exception e){fail(e);}
                }
                public void onCaptureFailed(CameraCaptureSession s,CaptureRequest r,CaptureFailure failure){fail(new IllegalStateException("Capture failed index="+r.getTag()+" reason="+failure.getReason()+" imageCaptured="+failure.wasImageCaptured()));}
                public void onCaptureBufferLost(CameraCaptureSession s,CaptureRequest r,Surface target,long frameNumber){fail(new IllegalStateException("Capture buffer lost frame "+frameNumber));}
            };
            if(expected>1)session.captureBurst(requests,callback,worker);else session.capture(requests.get(0),callback,worker);
        }catch(Exception e){fail(e);}
    }
    void pair(long timestamp) throws Exception {
        if(!images.containsKey(timestamp)||!results.containsKey(timestamp))return;
        Image image=images.remove(timestamp);TotalCaptureResult result=results.remove(timestamp);int index=(Integer)result.getRequest().getTag();String prefix="frame-"+index;
        long begin=SystemClock.elapsedRealtimeNanos();File dng=new File(runDir,prefix+".dng");
        try(DngCreator creator=new DngCreator(characteristics,result);FileOutputStream out=new FileOutputStream(dng)) {
            creator.setOrientation(1); // Explicit unrotated sensor axes; avoid undefined default TIFF value.
            creator.setDescription("Shutrwise throwaway Camera2 probe; camera "+cameraId+"; "+mode+" frame "+index);
            creator.writeImage(out,image);
        }finally{image.close();}
        JSONObject meta=new JSONObject();put(meta,"index",index);put(meta,"camera_id",cameraId);put(meta,"plan",plans.get(index));put(meta,"result",resultJson(result));put(meta,"sensor_timestamp_ns",timestamp);put(meta,"capture_started_timestamp_ns",started.get(index));put(meta,"dng_write_duration_ns",SystemClock.elapsedRealtimeNanos()-begin);put(meta,"dng_bytes",dng.length());put(meta,"dng_orientation",1);put(meta,"orientation_policy","unrotated sensor axes");put(meta,"frame_number",result.getFrameNumber());file(new File(runDir,prefix+"-result.json"),meta);
        written++;put(report,"dngs_written",written);log("SAVING");
        if(written==expected){finished=true;log("FINISHED");cleanup();}
    }
    void fail(Exception e){if(finished)return;finished=true;put(report,"error",e.toString());log("FAILED");Log.e("ShutrwiseProbe","Capture failed",e);cleanup();}
    void cleanup(){
        if(session!=null){session.close();session=null;}
        if(camera!=null){camera.close();camera=null;}
        for(Image image:images.values())image.close();images.clear();results.clear();
        if(reader!=null){reader.close();reader=null;}
        if(previewSurface!=null){previewSurface.release();previewSurface=null;}
    }
    @Override public void onDestroy(){super.onDestroy();if(worker!=null)worker.post(()->{if(!finished&&camera!=null)fail(new IllegalStateException("Activity destroyed"));cleanup();thread.quitSafely();});}
}
